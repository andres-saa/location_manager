"""
Endpoints para gestionar la configuración de la aplicación
"""
from fastapi import APIRouter
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.schemas.app_config import AppConfigUpdate, AppConfigResponse
from app.storage.json_storage import get_app_config, update_app_config

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("/", response_model=AppConfigResponse)
async def get_config():
    """
    Obtiene la configuración actual de la aplicación
    """
    config = get_app_config()
    return AppConfigResponse(
        validation_mode=config.get('validation_mode', 'polygons'),
        colombia_delivery_mode=config.get('colombia_delivery_mode', 'cargo'),
        max_delivery_distance_km=config.get('max_delivery_distance_km'),
        updated_at=config.get('updated_at', '')
    )


@router.put("/", response_model=AppConfigResponse)
async def update_config(config_update: AppConfigUpdate):
    """
    Actualiza la configuración de la aplicación
    """
    update_data = {
        'validation_mode': config_update.validation_mode
    }
    # Solo actualizar colombia_delivery_mode si se proporciona
    if config_update.colombia_delivery_mode is not None:
        update_data['colombia_delivery_mode'] = config_update.colombia_delivery_mode
    # Solo actualizar max_delivery_distance_km si se proporciona
    if config_update.max_delivery_distance_km is not None:
        update_data['max_delivery_distance_km'] = config_update.max_delivery_distance_km
    
    updated_config = update_app_config(update_data)
    return AppConfigResponse(
        validation_mode=updated_config.get('validation_mode', 'polygons'),
        colombia_delivery_mode=updated_config.get('colombia_delivery_mode', 'cargo'),
        max_delivery_distance_km=updated_config.get('max_delivery_distance_km'),
        updated_at=updated_config.get('updated_at', '')
    )
