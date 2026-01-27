"""
Servicio para obtener y filtrar sedes desde la API externa
"""
import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import settings
from app.storage.json_storage import (
    get_sites_cache, 
    save_sites_cache, 
    is_cache_valid, 
    get_picking_point_by_site_id,
    get_picking_point,
    update_picking_point as update_storage_pp
)
from app.services.rappi_picking_points import update_picking_point as update_rappi_pp

# Timezones permitidos por país
ALLOWED_TIMEZONES = [
    "America/Bogota",      # Colombia
    "America/New_York",     # Estados Unidos
    "Europe/Madrid"         # España
]

# Intervalo de actualización del caché en segundos (3 minutos)
CACHE_UPDATE_INTERVAL = 180

# Lock para evitar actualizaciones concurrentes
_cache_lock = asyncio.Lock()


async def fetch_sites() -> List[Dict]:
    """
    Obtiene todas las sedes desde la API externa
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.sites_api_url)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Error al obtener sedes: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP al obtener sedes: {e}")
        return []


def filter_sites(sites: List[Dict], excluded_ids: Optional[List[int]] = None) -> List[Dict]:
    """
    Filtra las sedes según los criterios:
    - time_zone debe estar en ALLOWED_TIMEZONES (Colombia, USA, España)
    - show_on_web debe ser True
    - Excluye los site_ids especificados
    """
    if excluded_ids is None:
        excluded_ids = settings.excluded_site_ids_list
    
    filtered = []
    for site in sites:
        # Filtrar por timezone (Colombia, USA, España)
        if site.get("time_zone") not in ALLOWED_TIMEZONES:
            continue
        
        # Filtrar por show_on_web
        if site.get("show_on_web") is not True:
            continue
        
        # Excluir por site_id
        if site.get("site_id") in excluded_ids:
            continue
        
        filtered.append(site)
    
    return filtered


def _get_site_key_fields(site: Dict) -> Dict:
    """
    Extrae los campos clave de una sede para comparación
    """
    return {
        'site_id': site.get('site_id'),
        'site_name': site.get('site_name'),
        'site_address': site.get('site_address'),
        'site_phone': site.get('site_phone'),
        'email_address': site.get('email_address'),
        'location': site.get('location'),  # [lat, lng]
        'city_name': site.get('city_name')
    }


def _site_has_changes(old_site: Dict, new_site: Dict) -> bool:
    """
    Compara dos versiones de una sede y determina si hay cambios en campos relevantes
    """
    old_fields = _get_site_key_fields(old_site)
    new_fields = _get_site_key_fields(new_site)
    
    # Comparar cada campo
    if old_fields['site_name'] != new_fields['site_name']:
        return True
    if old_fields['site_address'] != new_fields['site_address']:
        return True
    if old_fields['site_phone'] != new_fields['site_phone']:
        return True
    if old_fields['email_address'] != new_fields['email_address']:
        return True
    if old_fields['city_name'] != new_fields['city_name']:
        return True
    
    # Comparar location (coordenadas)
    old_location = old_fields['location']
    new_location = new_fields['location']
    if old_location != new_location:
        # Si ambos son listas, comparar valores
        if isinstance(old_location, list) and isinstance(new_location, list):
            if len(old_location) == 2 and len(new_location) == 2:
                if abs(old_location[0] - new_location[0]) > 0.0001 or abs(old_location[1] - new_location[1]) > 0.0001:
                    return True
        elif old_location != new_location:
            return True
    
    return False


async def _auto_relink_picking_point(site: Dict, picking_point: Dict) -> bool:
    """
    Hace relink automático de un picking point cuando la sede cambió
    """
    try:
        rappi_pp_id = picking_point.get('rappi_picking_point_id')
        if not rappi_pp_id:
            print(f"No se puede hacer relink automático: picking point {picking_point.get('id')} no tiene rappi_picking_point_id")
            return False
        
        # Preparar datos actualizados desde la sede
        updated_lat = 0.0
        updated_lng = 0.0
        if site.get('location') and isinstance(site['location'], list) and len(site['location']) == 2:
            updated_lat = site['location'][0]
            updated_lng = site['location'][1]
        
        updated_address = site.get('site_address') or ''
        updated_city = site.get('city_name') or ''
        
        site_phone = site.get('site_phone') or ''
        if isinstance(site_phone, str) and site_phone.startswith('+'):
            updated_phone = site_phone.replace('+', '')
        else:
            updated_phone = str(site_phone) if site_phone else ''
        
        updated_name = site.get('site_name') or ''
        updated_contact_email = site.get('email_address') or ''
        updated_contact_name = site.get('site_name') or 'Contacto'
        
        # Actualizar en Rappi
        rappi_result = await update_rappi_pp(
            picking_point_id=rappi_pp_id,
            lat=updated_lat,
            lng=updated_lng,
            address=updated_address,
            city=updated_city,
            phone=updated_phone,
            zip_code='',
            status=picking_point.get('status', 1),
            name=updated_name,
            contact_name=updated_contact_name,
            contact_email=updated_contact_email,
            preparation_time=30,
            external_id=picking_point.get('external_id') or f"PP_{site.get('site_id')}",
            rappi_store_id=None,
            default_tip=500,
            handshake_enabled=True,
            return_enabled=True,
            handoff_enabled=True
        )
        
        if not rappi_result:
            print(f"Error al hacer relink automático del picking point {picking_point.get('id')} en Rappi")
            return False
        
        # Actualizar en storage local
        storage_data = {
            'site_id': site.get('site_id'),
            'external_id': picking_point.get('external_id') or f"PP_{site.get('site_id')}",
            'name': updated_name,
            'address': updated_address,
            'lat': updated_lat,
            'lng': updated_lng,
            'city': updated_city,
            'phone': updated_phone,
            'status': picking_point.get('status', 1)
        }
        
        pp_id = picking_point.get('id')
        if pp_id:
            update_storage_pp(pp_id, storage_data)
            print(f"✅ Relink automático exitoso para picking point {pp_id} (sede {site.get('site_id')})")
            return True
        
        return False
    except Exception as e:
        print(f"Error en relink automático para picking point {picking_point.get('id')}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def _update_cache() -> List[Dict]:
    """
    Actualiza el caché de sedes desde la API y hace relink automático si hay cambios
    """
    # Obtener versión anterior de las sedes
    old_cache_data = get_sites_cache()
    old_sites = old_cache_data.get('sites', []) if old_cache_data else []
    
    # Obtener nuevas sedes
    sites = await fetch_sites()
    filtered_sites = filter_sites(sites, excluded_ids=[32])
    
    # Crear un diccionario de sedes antiguas por site_id para comparación rápida
    old_sites_dict = {site.get('site_id'): site for site in old_sites if site.get('site_id')}
    
    # Comparar y hacer relink automático si hay cambios
    for new_site in filtered_sites:
        site_id = new_site.get('site_id')
        if not site_id:
            continue
        
        old_site = old_sites_dict.get(site_id)
        if old_site and _site_has_changes(old_site, new_site):
            # La sede cambió, verificar si tiene picking point
            picking_point = get_picking_point_by_site_id(site_id)
            if picking_point and picking_point.get('rappi_picking_point_id'):
                print(f"🔄 Detectado cambio en sede {site_id} ({new_site.get('site_name')}). Haciendo relink automático...")
                await _auto_relink_picking_point(new_site, picking_point)
    
    # Guardar nueva versión de las sedes
    save_sites_cache(filtered_sites)
    return filtered_sites


def _enrich_sites_with_picking_points(sites: List[Dict]) -> List[Dict]:
    """
    Enriquece las sedes con información del picking point asociado (external_id)
    """
    enriched_sites = []
    for site in sites:
        site_id = site.get('site_id')
        if site_id:
            picking_point = get_picking_point_by_site_id(site_id)
            if picking_point:
                # Agregar external_id del picking point a la sede
                site_copy = site.copy()
                site_copy['picking_point_external_id'] = picking_point.get('external_id')
                enriched_sites.append(site_copy)
            else:
                enriched_sites.append(site)
        else:
            enriched_sites.append(site)
    return enriched_sites


async def get_available_sites(force_refresh: bool = False) -> List[Dict]:
    """
    Obtiene las sedes disponibles desde el caché o la API
    Enriquece las sedes con el external_id del picking point asociado si existe
    
    Args:
        force_refresh: Si es True, fuerza la actualización del caché
    """
    async with _cache_lock:
        # Si el caché es válido y no se fuerza actualización, usar caché
        if not force_refresh and is_cache_valid(CACHE_UPDATE_INTERVAL):
            cache_data = get_sites_cache()
            if cache_data and cache_data.get('sites'):
                sites = cache_data['sites']
                # Enriquecer con información de picking points
                return _enrich_sites_with_picking_points(sites)
        
        # Actualizar caché
        sites = await _update_cache()
        # Enriquecer con información de picking points
        return _enrich_sites_with_picking_points(sites)


async def refresh_cache_background():
    """
    Tarea en segundo plano que actualiza el caché cada 3 minutos
    """
    while True:
        try:
            await asyncio.sleep(CACHE_UPDATE_INTERVAL)
            await _update_cache()
            print(f"Caché de sedes actualizado: {datetime.now().isoformat()}")
        except Exception as e:
            print(f"Error actualizando caché de sedes: {e}")
            # Continuar intentando incluso si hay error
            await asyncio.sleep(60)  # Esperar 1 minuto antes de reintentar


def get_site_by_id(sites: List[Dict], site_id: int) -> Optional[Dict]:
    """
    Obtiene una sede por su site_id
    """
    for site in sites:
        if site.get("site_id") == site_id:
            return site
    return None
