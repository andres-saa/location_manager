from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.storage.json_storage import (
    get_all_polygons,
    get_polygon,
    get_polygon_by_site_id,
    create_polygon as create_polygon_storage,
    update_polygon as update_polygon_storage,
    delete_polygon as delete_polygon_storage
)
from app.schemas.polygon import PolygonCreate, PolygonUpdate, PolygonResponse
from app.utils.geometry import validate_polygon_coordinates
from app.services.sites import get_available_sites, get_site_by_id
from app.utils.country_filter import filter_polygons_by_country, Country
from typing import Optional
from fastapi import Query

router = APIRouter(prefix="/polygons", tags=["Polygons"])

def _dict_to_polygon_response(polygon_dict: dict) -> PolygonResponse:
    """Convierte un diccionario a PolygonResponse"""
    return PolygonResponse(
        id=polygon_dict['id'],
        name=polygon_dict['name'],
        description=polygon_dict.get('description'),
        coordinates=polygon_dict['coordinates'],
        color=polygon_dict.get('color', '#FF0000'),
        site_id=polygon_dict.get('site_id'),
        country=polygon_dict.get('country'),
        created_at=datetime.fromisoformat(polygon_dict['created_at']) if polygon_dict.get('created_at') else datetime.now(),
        updated_at=datetime.fromisoformat(polygon_dict['updated_at']) if polygon_dict.get('updated_at') else None
    )

@router.get("/", response_model=List[PolygonResponse])
async def get_polygons(
    skip: int = 0, 
    limit: int = 100,
    country: Optional[Country] = Query(None, description="Filtrar por país: 'colombia', 'usa', 'spain'")
):
    """
    Obtener todos los polígonos, opcionalmente filtrados por país.
    
    Args:
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        country: País para filtrar los polígonos ('colombia', 'usa', 'spain')
    """
    polygons = get_all_polygons()
    
    # Filtrar por país si se especifica
    if country:
        sites = await get_available_sites()
        polygons = filter_polygons_by_country(polygons, sites, country)
    
    # Aplicar paginación
    polygons = polygons[skip:skip + limit]
    return [_dict_to_polygon_response(p) for p in polygons]

@router.get("/{polygon_id}", response_model=PolygonResponse)
async def get_polygon_by_id(polygon_id: int):
    """Obtener un polígono por ID"""
    polygon_dict = get_polygon(polygon_id)
    if not polygon_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Polígono con ID {polygon_id} no encontrado"
        )
    return _dict_to_polygon_response(polygon_dict)

@router.post("/", response_model=PolygonResponse, status_code=status.HTTP_201_CREATED)
async def create_polygon(polygon: PolygonCreate):
    """Crear un nuevo polígono"""
    # Validar coordenadas
    if not validate_polygon_coordinates(polygon.coordinates):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coordenadas inválidas. Se requieren al menos 3 puntos [lat, lng]"
        )
    
    # Validar que la sede existe si se especifica
    if polygon.site_id:
        sites = await get_available_sites()
        site = get_site_by_id(sites, polygon.site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con ID {polygon.site_id} no encontrada o no disponible"
            )
        
        # Verificar que no haya otro polígono con la misma sede
        existing_polygon = get_polygon_by_site_id(polygon.site_id)
        if existing_polygon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La sede con ID {polygon.site_id} ya está asociada al polígono '{existing_polygon.get('name')}' (ID: {existing_polygon.get('id')})"
            )
    
    polygon_data = polygon.model_dump()
    polygon_dict = create_polygon_storage(polygon_data)
    return _dict_to_polygon_response(polygon_dict)

@router.put("/{polygon_id}", response_model=PolygonResponse)
async def update_polygon(
    polygon_id: int,
    polygon_update: PolygonUpdate
):
    """Actualizar un polígono"""
    # Validar coordenadas si se están actualizando
    if polygon_update.coordinates is not None:
        if not validate_polygon_coordinates(polygon_update.coordinates):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coordenadas inválidas. Se requieren al menos 3 puntos [lat, lng]"
            )
    
    # Validar que la sede existe si se está actualizando
    if polygon_update.site_id is not None:
        sites = await get_available_sites()
        site = get_site_by_id(sites, polygon_update.site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con ID {polygon_update.site_id} no encontrada o no disponible"
            )
        
        # Verificar que no haya otro polígono con la misma sede (excluyendo el actual)
        existing_polygon = get_polygon_by_site_id(polygon_update.site_id, exclude_polygon_id=polygon_id)
        if existing_polygon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La sede con ID {polygon_update.site_id} ya está asociada al polígono '{existing_polygon.get('name')}' (ID: {existing_polygon.get('id')})"
            )
    
    update_data = polygon_update.model_dump(exclude_unset=True)
    polygon_dict = update_polygon_storage(polygon_id, update_data)
    
    if not polygon_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Polígono con ID {polygon_id} no encontrado"
        )
    
    return _dict_to_polygon_response(polygon_dict)

@router.delete("/{polygon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_polygon(polygon_id: int):
    """Eliminar un polígono"""
    success = delete_polygon_storage(polygon_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Polígono con ID {polygon_id} no encontrado"
        )
    return None
