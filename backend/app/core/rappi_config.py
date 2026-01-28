"""
Configuración centralizada para los endpoints de Rappi Cargo
Permite cambiar fácilmente entre desarrollo y producción
"""
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import settings

# Ambiente: 'dev' o 'prod'
RAPPI_ENV = settings.rappi_env.lower() if hasattr(settings, 'rappi_env') else 'dev'

# Base URLs según el ambiente
RAPPI_BASE_URLS = {
    'dev': 'https://microservices.dev.rappi.com',
    'prod': 'https://microservices.dev.rappi.com'  # Ajustar cuando se conozca la URL de producción
}

# Base URL actual según el ambiente
RAPPI_BASE_URL = RAPPI_BASE_URLS.get(RAPPI_ENV, RAPPI_BASE_URLS['dev'])

# Endpoints de Rappi Cargo
RAPPI_ENDPOINTS = {
    'picking_point': f'{RAPPI_BASE_URL}/api/cargo-api-gateway/picking-point',
    'picking_point_list': f'{RAPPI_BASE_URL}/api/cargo-api-gateway/picking-point/list',
    'order_validate': f'{RAPPI_BASE_URL}/api/cargo-api-gateway/v3/order-validate',
}

# Token de usuario (desde settings)
RAPPI_USER_TOKEN = settings.rappi_user_token

# Funciones helper para obtener endpoints
def get_picking_point_url() -> str:
    """Retorna la URL para crear/actualizar picking points"""
    return RAPPI_ENDPOINTS['picking_point']

def get_picking_point_list_url() -> str:
    """Retorna la URL para listar picking points"""
    return RAPPI_ENDPOINTS['picking_point_list']

def get_order_validate_url() -> str:
    """Retorna la URL para validar órdenes"""
    return RAPPI_ENDPOINTS['order_validate']

def get_user_token() -> str:
    """Retorna el token de usuario para autenticación"""
    return RAPPI_USER_TOKEN
