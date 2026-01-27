"""
Servicio para geocodificación usando Google Maps Geocoding API
"""
import httpx
from typing import Optional, Dict, Tuple, Any
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import settings

# URL de la API de Geocodificación de Google Maps
GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


async def geocode_address(address: str, api_key: str, city: Optional[str] = None, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convierte una dirección a coordenadas (lat, lng) usando Google Maps Geocoding API
    
    Args:
        address: Dirección a geocodificar
        api_key: API Key de Google Maps
        city: Ciudad (opcional, mejora la precisión)
        country: País (opcional, mejora la precisión)
    
    Returns:
        Dict con 'latitude', 'longitude' y 'formatted_address' si se encuentra, None si no
    """
    if not api_key:
        raise ValueError("Google Maps API Key no configurada")
    
    try:
        # Construir la dirección completa con ciudad y país si están disponibles
        full_address = address
        if city:
            full_address = f"{full_address}, {city}"
        if country:
            full_address = f"{full_address}, {country}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                'address': full_address,
                'key': api_key
            }
            response = await client.get(GEOCODING_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                result = data['results'][0]
                location = result['geometry']['location']
                formatted_address = result.get('formatted_address', address)
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': formatted_address
                }
            else:
                print(f"Error en geocodificación: {data.get('status')} - {data.get('error_message', '')}")
                return None
    except httpx.RequestError as e:
        print(f"Error al geocodificar dirección: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP al geocodificar: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado en geocodificación: {e}")
        return None
