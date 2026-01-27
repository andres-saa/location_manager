from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import asyncio

# Agregar el directorio padre al path para importaciones absolutas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.router import router
from app.storage.json_storage import DATA_DIR
from app.services.sites import refresh_cache_background, get_available_sites

# Asegurar que el directorio de datos existe
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="LocationManager API",
    description="API para gestión de polígonos y ubicaciones con Google Maps",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue dev server
        "http://localhost:3000",  # Nuxt default
        "http://localhost:3001",  # Nuxt alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router, prefix="/api", tags=["api"])


@app.on_event("startup")
async def startup_event():
    """
    Inicializa el caché de sedes al arrancar la aplicación
    y lanza la tarea en segundo plano para actualizarlo cada 3 minutos
    """
    # Cargar caché inicial si no existe o está expirado
    print("Inicializando caché de sedes...")
    await get_available_sites(force_refresh=True)
    
    # Iniciar tarea en segundo plano para actualizar el caché
    asyncio.create_task(refresh_cache_background())
    print("Tarea de actualización de caché iniciada (cada 3 minutos)")

@app.get("/")
async def root():
    return {
        "message": "LocationManager API está funcionando",
        "docs": "/docs",
        "endpoints": {
            "polygons": "/api/polygons",
            "check": "/api/check/address",
            "sites": "/api/sites"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
