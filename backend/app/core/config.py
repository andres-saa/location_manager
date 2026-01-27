from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "LocationManager"
    debug: bool = True
    database_url: str = "sqlite:///./locationmanager.db"
    sites_api_url: str = "https://backend.salchimonster.com/sites"
    excluded_site_ids: str = ""  # IDs separados por coma, ej: "18,14,20,21"
    google_maps_api_key: str = ""  # API Key de Google Maps para geocodificación
    rappi_env: str = "dev"  # Ambiente de Rappi: 'dev' o 'prod'
    rappi_user_token: str = "8f4e1480ebdafc50245cbb590bbc8411"  # Token de usuario para API de Rappi
    
    @property
    def excluded_site_ids_list(self) -> List[int]:
        """Convierte la cadena de IDs excluidos a una lista de enteros"""
        if not self.excluded_site_ids:
            return []
        return [int(id.strip()) for id in self.excluded_site_ids.split(",") if id.strip()]
    
    class Config:
        env_file = ".env"

settings = Settings()
