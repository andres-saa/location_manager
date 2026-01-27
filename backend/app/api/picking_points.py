"""
Endpoints para gestionar picking points de Rappi Cargo
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.schemas.picking_point import PickingPointCreate, PickingPointResponse
from app.services.rappi_picking_points import (
    create_picking_point as create_rappi_pp, 
    list_picking_points as list_rappi_pp,
    update_picking_point as update_rappi_pp,
    delete_picking_point as delete_rappi_pp
)
from app.services.sites import get_available_sites, get_site_by_id
from app.storage.json_storage import (
    create_picking_point as create_storage_pp,
    get_all_picking_points,
    get_picking_points_by_site_id,
    get_picking_point_by_site_id,
    get_picking_point,
    update_picking_point as update_storage_pp,
    delete_picking_point as delete_storage_pp
)
from app.utils.country_filter import filter_picking_points_by_country, Country
from typing import Optional
from fastapi import Query
from datetime import datetime

router = APIRouter(prefix="/picking-points", tags=["Picking Points"])


def _dict_to_picking_point_response(pp_dict: dict) -> PickingPointResponse:
    """Convierte un diccionario a PickingPointResponse"""
    try:
        return PickingPointResponse(
            id=pp_dict.get('id', 0),
            site_id=pp_dict.get('site_id', 0),
            rappi_picking_point_id=pp_dict.get('rappi_picking_point_id'),
            external_id=pp_dict.get('external_id'),
            name=pp_dict.get('name'),
            address=pp_dict.get('address'),
            lat=pp_dict.get('lat'),
            lng=pp_dict.get('lng'),
            city=pp_dict.get('city'),
            phone=pp_dict.get('phone'),
            status=pp_dict.get('status'),
            created_at=pp_dict.get('created_at', datetime.now().isoformat()),
            updated_at=pp_dict.get('updated_at')
        )
    except Exception as e:
        print(f"Error al convertir picking point a respuesta: {e}")
        print(f"Datos del picking point: {pp_dict}")
        raise


@router.get("/", response_model=List[PickingPointResponse])
async def get_picking_points(
    site_id: Optional[int] = None,
    country: Optional[Country] = Query(None, description="Filtrar por país: 'colombia', 'usa', 'spain'")
):
    """
    Obtiene todos los picking points, opcionalmente filtrados por sede o país.
    
    Args:
        site_id: ID de la sede para filtrar
        country: País para filtrar los picking points ('colombia', 'usa', 'spain')
    """
    try:
        if site_id:
            picking_points = get_picking_points_by_site_id(site_id)
        else:
            picking_points = get_all_picking_points()
        
        # Filtrar por país si se especifica
        if country:
            sites = await get_available_sites()
            picking_points = filter_picking_points_by_country(picking_points, sites, country)
        
        return [_dict_to_picking_point_response(pp) for pp in picking_points]
    except Exception as e:
        print(f"Error al obtener picking points: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener picking points: {str(e)}"
        )


@router.post("/", response_model=PickingPointResponse, status_code=status.HTTP_201_CREATED)
async def create_picking_point(picking_point: PickingPointCreate):
    """
    Crea un picking point en Rappi Cargo y lo asocia a una sede
    """
    # Validar que la sede existe
    sites = await get_available_sites()
    site = get_site_by_id(sites, picking_point.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede con ID {picking_point.site_id} no encontrada o no disponible"
        )
    
    # Validar relación 1 a 1: verificar que no exista ya un picking point para esta sede
    existing_pp = get_picking_point_by_site_id(picking_point.site_id)
    if existing_pp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un picking point para la sede con ID {picking_point.site_id}. La relación es 1 a 1."
        )
    
    # Crear picking point en Rappi
    rappi_result = await create_rappi_pp(
        lat=picking_point.lat,
        lng=picking_point.lng,
        address=picking_point.address,
        city=picking_point.city,
        phone=picking_point.phone,
        zip_code=picking_point.zip_code,
        status=picking_point.status,
        name=picking_point.name,
        contact_name=picking_point.contact_name,
        contact_email=picking_point.contact_email,
        preparation_time=picking_point.preparation_time,
        external_id=picking_point.external_id,
        rappi_store_id=picking_point.rappi_store_id,
        default_tip=picking_point.default_tip,
        handshake_enabled=picking_point.handshake_enabled,
        return_enabled=picking_point.return_enabled,
        handoff_enabled=picking_point.handoff_enabled
    )
    
    if not rappi_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear picking point en Rappi Cargo. No se recibió respuesta de la API."
        )
    
    # Extraer el ID del picking point creado en Rappi
    # La API puede retornar el ID directamente o dentro de un objeto
    rappi_pp_id = None
    if isinstance(rappi_result, dict):
        rappi_pp_id = rappi_result.get('id') or rappi_result.get('picking_point_id')
    elif isinstance(rappi_result, (int, str)):
        rappi_pp_id = int(rappi_result) if str(rappi_result).isdigit() else None
    
    # Guardar en storage local asociado a la sede
    storage_data = {
        'site_id': picking_point.site_id,
        'rappi_picking_point_id': rappi_pp_id,
        'external_id': picking_point.external_id,
        'name': picking_point.name,
        'address': picking_point.address,
        'lat': picking_point.lat,
        'lng': picking_point.lng,
        'city': picking_point.city,
        'phone': picking_point.phone,
        'status': picking_point.status
    }
    
    stored_pp = create_storage_pp(storage_data)
    return _dict_to_picking_point_response(stored_pp)


@router.get("/rappi", response_model=List[Dict])
async def get_rappi_picking_points():
    """
    Obtiene todos los picking points desde Rappi Cargo
    """
    picking_points = await list_rappi_pp()
    return picking_points


@router.put("/{picking_point_id}/relink", response_model=PickingPointResponse)
async def relink_picking_point(picking_point_id: int, picking_point: PickingPointCreate):
    """
    Revincula/actualiza un picking point existente en Rappi Cargo.
    Fuerza la actualización de la cache de sedes antes de actualizar.
    """
    try:
        # Obtener el picking point local
        local_pp = get_picking_point(picking_point_id)
        if not local_pp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Picking point con ID {picking_point_id} no encontrado"
            )
        
        # Verificar que tenga un rappi_picking_point_id
        rappi_pp_id = local_pp.get('rappi_picking_point_id')
        if not rappi_pp_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este picking point no tiene un ID de Rappi asociado. No se puede revincular."
            )
        
        # FORZAR actualización de la cache de sedes (aunque no hayan pasado los 3 minutos)
        sites = await get_available_sites(force_refresh=True)
        site = get_site_by_id(sites, picking_point.site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con ID {picking_point.site_id} no encontrada o no disponible"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en relink_picking_point (validación inicial): {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar datos: {str(e)}"
        )
    
    # Actualizar los datos del picking point con la información más reciente de la sede
    # si los campos están vacíos o usan valores por defecto
    updated_lat = picking_point.lat
    updated_lng = picking_point.lng
    updated_address = picking_point.address
    updated_city = picking_point.city
    updated_phone = picking_point.phone
    updated_name = picking_point.name
    updated_contact_email = picking_point.contact_email
    
    # Usar datos de la sede si los campos están vacíos o son valores por defecto
    if site.get('location') and isinstance(site['location'], list) and len(site['location']) == 2:
        if not updated_lat or updated_lat == 0:
            updated_lat = site['location'][0]
        if not updated_lng or updated_lng == 0:
            updated_lng = site['location'][1]
    
    if site.get('site_address') and (not updated_address or (isinstance(updated_address, str) and updated_address.strip() == '')):
        updated_address = site['site_address'] or ''
    
    if site.get('city_name') and (not updated_city or (isinstance(updated_city, str) and updated_city.strip() == '')):
        updated_city = site['city_name'] or ''
    
    if site.get('site_phone'):
        site_phone = site['site_phone']
        if site_phone and (not updated_phone or updated_phone == '' or (isinstance(updated_phone, str) and updated_phone.strip() == '')):
            # Remover el + si existe
            if isinstance(site_phone, str):
                updated_phone = site_phone.replace('+', '') if site_phone.startswith('+') else site_phone
            else:
                updated_phone = str(site_phone) if site_phone else ''
    
    if site.get('site_name') and (not updated_name or (isinstance(updated_name, str) and updated_name.strip() == '')):
        updated_name = site['site_name'] or ''
    
    if site.get('email_address') and (not updated_contact_email or (isinstance(updated_contact_email, str) and updated_contact_email.strip() == '')):
        updated_contact_email = site['email_address'] or ''
    
    # Actualizar picking point en Rappi con los datos actualizados de la sede
    rappi_result = await update_rappi_pp(
        picking_point_id=rappi_pp_id,
        lat=updated_lat,
        lng=updated_lng,
        address=updated_address,
        city=updated_city,
        phone=updated_phone,
        zip_code=picking_point.zip_code,
        status=picking_point.status,
        name=updated_name,
        contact_name=picking_point.contact_name or site.get('site_name', 'Contacto'),
        contact_email=updated_contact_email,
        preparation_time=picking_point.preparation_time,
        external_id=picking_point.external_id,
        rappi_store_id=picking_point.rappi_store_id,
        default_tip=picking_point.default_tip,
        handshake_enabled=picking_point.handshake_enabled,
        return_enabled=picking_point.return_enabled,
        handoff_enabled=picking_point.handoff_enabled
    )
    
    if not rappi_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar picking point en Rappi Cargo. No se recibió respuesta de la API."
        )
    
    try:
        # Actualizar en storage local con los datos actualizados
        storage_data = {
            'site_id': picking_point.site_id,
            'external_id': picking_point.external_id,
            'name': updated_name or '',
            'address': updated_address or '',
            'lat': updated_lat or 0.0,
            'lng': updated_lng or 0.0,
            'city': updated_city or '',
            'phone': updated_phone or '',
            'status': picking_point.status or 1
        }
        
        updated_pp = update_storage_pp(picking_point_id, storage_data)
        if not updated_pp:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar picking point en el almacenamiento local"
            )
        
        return _dict_to_picking_point_response(updated_pp)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en relink_picking_point (actualización final): {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar picking point: {str(e)}"
        )


@router.delete("/{picking_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_picking_point(picking_point_id: int):
    """
    Desvincula/elimina un picking point de Rappi Cargo.
    Esto eliminará el picking point tanto en Rappi como en el almacenamiento local.
    """
    try:
        # Obtener el picking point local
        local_pp = get_picking_point(picking_point_id)
        if not local_pp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Picking point con ID {picking_point_id} no encontrado"
            )
        
        # Verificar que tenga un rappi_picking_point_id
        rappi_pp_id = local_pp.get('rappi_picking_point_id')
        print(f"Picking point local ID: {picking_point_id}")
        print(f"Picking point local data: {local_pp}")
        print(f"Rappi picking point ID a eliminar: {rappi_pp_id}")
        
        if not rappi_pp_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este picking point no tiene un ID de Rappi asociado. No se puede desvincular."
            )
        
        # Eliminar picking point en Rappi usando el ID interno de Rappi
        deleted = await delete_rappi_pp(rappi_pp_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar picking point en Rappi Cargo. No se pudo completar la operación."
            )
        
        # Eliminar del almacenamiento local
        deleted_local = delete_storage_pp(picking_point_id)
        if not deleted_local:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar picking point del almacenamiento local"
            )
        
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en delete_picking_point: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desvincular picking point: {str(e)}"
        )
