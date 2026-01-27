"""
Endpoints para gestionar sedes
"""
from fastapi import APIRouter, Query
from typing import List, Dict, Optional, Literal

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.sites import get_available_sites
from app.utils.country_filter import filter_sites_by_country, Country

router = APIRouter(prefix="/sites", tags=["Sites"])

@router.get("/", response_model=List[Dict])
async def get_sites(
    force_refresh: bool = False,
    country: Optional[str] = Query(None, description="Filtrar por país: 'colombia', 'usa', 'spain'")
):
    """
    Obtiene las sedes disponibles filtradas por timezone y exclusiones.
    Las sedes incluyen el campo 'picking_point_external_id' si tienen un picking point asociado.
    
    Args:
        force_refresh: Si es True, fuerza la actualización del caché
        country: País para filtrar las sedes ('colombia', 'usa', 'spain')
    """
    sites = await get_available_sites(force_refresh=force_refresh)
    
    # Debug: Log del país solicitado y cantidad de sedes antes del filtro
    print(f"[DEBUG] get_sites - País solicitado: {country} (tipo: {type(country)})")
    print(f"[DEBUG] get_sites - Total de sedes antes del filtro: {len(sites)}")
    
    # Debug: Mostrar algunos timezones de ejemplo antes del filtro
    if sites:
        sample_timezones = set(site.get('time_zone') for site in sites[:5] if site.get('time_zone'))
        print(f"[DEBUG] get_sites - Timezones de ejemplo antes del filtro: {sample_timezones}")
    
    # Validar y convertir el país a tipo Country
    valid_countries = ['colombia', 'usa', 'spain']
    country_filter: Optional[Country] = None
    
    if country:
        country_lower = country.lower().strip()
        if country_lower in valid_countries:
            country_filter = country_lower  # type: ignore
            print(f"[DEBUG] get_sites - País validado: {country_filter}")
        else:
            print(f"[DEBUG] get_sites - ⚠️ País inválido recibido: {country}, ignorando filtro")
    
    # Filtrar por país si se especifica
    if country_filter:
        print(f"[DEBUG] get_sites - Aplicando filtro para país: {country_filter}")
        sites_before = len(sites)
        sites = filter_sites_by_country(sites, country_filter)
        print(f"[DEBUG] get_sites - Sedes después del filtro: {len(sites)} (de {sites_before})")
        
        # Debug: Mostrar timezones de las sedes filtradas
        if sites:
            timezones = set(site.get('time_zone') for site in sites if site.get('time_zone'))
            print(f"[DEBUG] get_sites - Timezones encontrados en sedes filtradas: {timezones}")
        else:
            print(f"[DEBUG] get_sites - ⚠️ No se encontraron sedes para el país {country_filter}")
    else:
        print(f"[DEBUG] get_sites - No se especificó país válido (country={country}), devolviendo todas las sedes")
    
    return sites


@router.post("/refresh", response_model=List[Dict])
async def refresh_sites():
    """
    Fuerza la actualización de la cache de sedes y retorna las sedes actualizadas.
    Útil para actualizar el picking_point_external_id después de crear/modificar picking points.
    """
    sites = await get_available_sites(force_refresh=True)
    return sites


@router.get("/cities", response_model=List[str])
async def get_cities(
    country: Optional[str] = Query(None, description="Filtrar por país: 'colombia', 'usa', 'spain'")
):
    """
    Obtiene la lista de ciudades únicas de las sedes disponibles.
    
    Args:
        country: País para filtrar las ciudades ('colombia', 'usa', 'spain')
    """
    sites = await get_available_sites()
    
    # Validar y convertir el país a tipo Country
    valid_countries = ['colombia', 'usa', 'spain']
    country_filter: Optional[Country] = None
    
    if country:
        country_lower = country.lower().strip()
        if country_lower in valid_countries:
            country_filter = country_lower  # type: ignore
    
    # Filtrar por país si se especifica
    if country_filter:
        sites = filter_sites_by_country(sites, country_filter)
    
    cities = set()
    for site in sites:
        city_name = site.get('city_name')
        if city_name:
            cities.add(city_name)
    return sorted(list(cities))
