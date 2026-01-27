from fastapi import APIRouter
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.api.polygons import router as polygons_router
# from app.api.locations import router as locations_router  # Deshabilitado - no se usa
from app.api.check import router as check_router
from app.api.sites import router as sites_router
from app.api.picking_points import router as picking_points_router
from app.api.app_config import router as app_config_router
from app.api.orders import router as orders_router
from app.api.site_tariffs import router as site_tariffs_router

router = APIRouter()

# Incluir todos los routers
router.include_router(polygons_router)
# router.include_router(locations_router)  # Deshabilitado - no se usa
router.include_router(check_router)
router.include_router(sites_router)
router.include_router(picking_points_router)
router.include_router(app_config_router)
router.include_router(orders_router)
router.include_router(site_tariffs_router)