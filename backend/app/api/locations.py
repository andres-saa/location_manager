from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.storage.json_storage import (
    get_all_locations,
    get_location as get_location_storage,
    get_locations_by_polygon,
    create_location as create_location_storage,
    update_location as update_location_storage,
    delete_location as delete_location_storage
)
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])

def _dict_to_location_response(location_dict: dict) -> LocationResponse:
    """Convierte un diccionario a LocationResponse"""
    return LocationResponse(
        id=location_dict['id'],
        name=location_dict['name'],
        description=location_dict.get('description'),
        latitude=location_dict['latitude'],
        longitude=location_dict['longitude'],
        address=location_dict.get('address'),
        polygon_id=location_dict.get('polygon_id'),
        created_at=datetime.fromisoformat(location_dict['created_at']) if location_dict.get('created_at') else datetime.now(),
        updated_at=datetime.fromisoformat(location_dict['updated_at']) if location_dict.get('updated_at') else None
    )

@router.get("/", response_model=List[LocationResponse])
async def get_locations(
    skip: int = 0,
    limit: int = 100,
    polygon_id: Optional[int] = None
):
    """Obtener todas las locaciones, opcionalmente filtradas por polígono"""
    if polygon_id:
        locations = get_locations_by_polygon(polygon_id)
    else:
        locations = get_all_locations()
    
    # Aplicar paginación
    locations = locations[skip:skip + limit]
    return [_dict_to_location_response(loc) for loc in locations]

@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int):
    """Obtener una locación por ID"""
    location_dict = get_location_storage(location_id)
    if not location_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locación con ID {location_id} no encontrada"
        )
    return _dict_to_location_response(location_dict)

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(location: LocationCreate):
    """Crear una nueva locación"""
    try:
        location_data = location.model_dump()
        location_dict = create_location_storage(location_data)
        return _dict_to_location_response(location_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location_update: LocationUpdate
):
    """Actualizar una locación"""
    try:
        update_data = location_update.model_dump(exclude_unset=True)
        location_dict = update_location_storage(location_id, update_data)
        
        if not location_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Locación con ID {location_id} no encontrada"
            )
        
        return _dict_to_location_response(location_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(location_id: int):
    """Eliminar una locación"""
    success = delete_location_storage(location_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locación con ID {location_id} no encontrada"
        )
    return None
