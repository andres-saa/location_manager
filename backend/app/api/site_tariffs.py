"""
Endpoints para gestionar tarifas de entrega por sede (USA y España)
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.schemas.site_tariff import SiteTariffCreate, SiteTariffUpdate, SiteTariffResponse
from app.storage.json_storage import (
    get_all_site_tariffs,
    get_site_tariff,
    create_site_tariff as create_storage_tariff,
    update_site_tariff as update_storage_tariff,
    delete_site_tariff as delete_storage_tariff
)
from app.services.sites import get_available_sites, get_site_by_id
from app.utils.country_filter import get_country_from_timezone, Country
from datetime import datetime

router = APIRouter(prefix="/site-tariffs", tags=["Site Tariffs"])


def _dict_to_tariff_response(tariff_dict: dict) -> SiteTariffResponse:
    """Convierte un diccionario a SiteTariffResponse"""
    return SiteTariffResponse(
        site_id=tariff_dict['site_id'],
        tariff_mode=tariff_dict.get('tariff_mode', 'fixed'),
        price_per_km=tariff_dict['price_per_km'],
        min_fee=tariff_dict['min_fee'],
        max_fee=tariff_dict.get('max_fee'),
        base_distance_km=tariff_dict.get('base_distance_km'),
        surcharge_per_km=tariff_dict.get('surcharge_per_km'),
        country=tariff_dict.get('country', 'unknown'),
        created_at=tariff_dict.get('created_at', datetime.now().isoformat()),
        updated_at=tariff_dict.get('updated_at')
    )


@router.get("/", response_model=List[SiteTariffResponse])
async def get_site_tariffs(
    site_id: Optional[int] = Query(None, description="Filtrar por site_id"),
    country: Optional[Country] = Query(None, description="Filtrar por país: 'colombia', 'usa', 'spain'")
):
    """
    Obtiene todas las tarifas de sedes, opcionalmente filtradas por sede o país.
    
    Args:
        site_id: ID de la sede para filtrar
        country: País para filtrar las tarifas ('colombia', 'usa', 'spain')
    """
    tariffs = get_all_site_tariffs()
    
    # Filtrar por site_id si se especifica
    if site_id:
        tariff = get_site_tariff(site_id)
        return [_dict_to_tariff_response(tariff)] if tariff else []
    
    # Filtrar por país si se especifica
    if country:
        # Obtener sedes del país
        sites = await get_available_sites()
        country_site_ids = set()
        for site in sites:
            site_country = get_country_from_timezone(site.get('time_zone'))
            if site_country == country:
                country_site_ids.add(site.get('site_id'))
        
        # Filtrar tarifas
        tariffs = [t for t in tariffs if t.get('site_id') in country_site_ids]
    
    return [_dict_to_tariff_response(t) for t in tariffs]


@router.get("/{site_id}", response_model=SiteTariffResponse)
async def get_site_tariff_by_id(site_id: int):
    """Obtiene la tarifa de una sede por site_id"""
    tariff = get_site_tariff(site_id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarifa para la sede {site_id} no encontrada"
        )
    return _dict_to_tariff_response(tariff)


@router.post("/", response_model=SiteTariffResponse, status_code=status.HTTP_201_CREATED)
async def create_site_tariff_endpoint(tariff: SiteTariffCreate):
    """
    Crea una nueva tarifa de entrega para una sede (solo USA y España).
    """
    # Validar que la sede existe
    sites = await get_available_sites()
    site = get_site_by_id(sites, tariff.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede con ID {tariff.site_id} no encontrada o no disponible"
        )
    
    # Validar que la sede es de USA, España o Colombia (si usa tarifa calculada)
    site_country = get_country_from_timezone(site.get('time_zone'))
    if site_country not in ['usa', 'spain', 'colombia']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Las tarifas personalizadas solo están disponibles para sedes de USA, España o Colombia (con modo calculado). Esta sede es de {site_country}."
        )
    
    # Si es Colombia, verificar que el modo de entrega sea 'calculated'
    if site_country == 'colombia':
        from app.storage.json_storage import get_app_config
        app_config = get_app_config()
        colombia_delivery_mode = app_config.get('colombia_delivery_mode', 'cargo')
        if colombia_delivery_mode != 'calculated':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las tarifas personalizadas para Colombia solo están disponibles cuando el modo de entrega es 'Tarifa Calculada'. Cambia la configuración en la sección 'Modo de Entrega'."
            )
    
    # Validar que max_fee >= min_fee si se proporciona
    if tariff.max_fee is not None and tariff.max_fee < tariff.min_fee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tarifa máxima no puede ser menor que la tarifa mínima"
        )
    
    # Validar campos de modo surcharge
    if tariff.tariff_mode == 'surcharge':
        if tariff.base_distance_km is None or tariff.surcharge_per_km is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para el modo 'surcharge' se requiere especificar 'base_distance_km' y 'surcharge_per_km'"
            )
    
    tariff_data = tariff.model_dump()
    tariff_data['country'] = site_country
    
    try:
        tariff_dict = create_storage_tariff(tariff_data)
        return _dict_to_tariff_response(tariff_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{site_id}", response_model=SiteTariffResponse)
async def update_site_tariff_endpoint(site_id: int, tariff_update: SiteTariffUpdate):
    """
    Actualiza la tarifa de entrega de una sede.
    """
    # Validar que la tarifa existe
    existing_tariff = get_site_tariff(site_id)
    if not existing_tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarifa para la sede {site_id} no encontrada"
        )
    
    # Validar que max_fee >= min_fee si se actualiza
    update_data = tariff_update.model_dump(exclude_unset=True)
    new_min_fee = update_data.get('min_fee', existing_tariff.get('min_fee'))
    new_max_fee = update_data.get('max_fee')
    if new_max_fee is not None:
        # Si se está actualizando max_fee, usar el nuevo valor
        if new_max_fee is not None and new_max_fee < new_min_fee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La tarifa máxima no puede ser menor que la tarifa mínima"
            )
    
    # Validar campos de modo surcharge si se está cambiando a ese modo
    new_tariff_mode = update_data.get('tariff_mode', existing_tariff.get('tariff_mode', 'fixed'))
    if new_tariff_mode == 'surcharge':
        base_distance = update_data.get('base_distance_km', existing_tariff.get('base_distance_km'))
        surcharge = update_data.get('surcharge_per_km', existing_tariff.get('surcharge_per_km'))
        if base_distance is None or surcharge is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para el modo 'surcharge' se requiere especificar 'base_distance_km' y 'surcharge_per_km'"
            )
    
    tariff_dict = update_storage_tariff(site_id, update_data)
    if not tariff_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarifa para la sede {site_id} no encontrada"
        )
    
    return _dict_to_tariff_response(tariff_dict)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_tariff_endpoint(site_id: int):
    """Elimina la tarifa de una sede"""
    success = delete_storage_tariff(site_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarifa para la sede {site_id} no encontrada"
        )
    return None
