"""
Utilidades para filtrar datos por país basado en timezone
"""
from typing import List, Dict, Optional, Literal

Country = Literal['colombia', 'usa', 'spain']

# Mapeo de timezones a países
TIMEZONE_TO_COUNTRY = {
    'America/Bogota': 'colombia',
    'America/New_York': 'usa',
    'Europe/Madrid': 'spain'
}

def get_country_from_timezone(timezone: Optional[str]) -> Optional[str]:
    """
    Obtiene el país basado en el timezone de una sede.
    
    Args:
        timezone: Timezone de la sede (ej: 'America/Bogota')
    
    Returns:
        'colombia', 'usa', 'spain' o None si no coincide
    """
    if not timezone:
        return None
    
    country = TIMEZONE_TO_COUNTRY.get(timezone)
    if not country:
        print(f"[DEBUG] get_country_from_timezone - Timezone '{timezone}' no está mapeado a ningún país")
    
    return country


def filter_sites_by_country(sites: List[Dict], country: Country) -> List[Dict]:
    """
    Filtra sedes por país basado en su timezone.
    
    Args:
        sites: Lista de sedes
        country: País a filtrar ('colombia', 'usa', 'spain')
    
    Returns:
        Lista de sedes filtradas
    """
    filtered = []
    print(f"[DEBUG] filter_sites_by_country - Filtrando {len(sites)} sedes para país: {country}")
    
    for site in sites:
        site_timezone = site.get('time_zone')
        site_country = get_country_from_timezone(site_timezone)
        
        # Debug para las primeras sedes
        if len(filtered) < 3:
            print(f"[DEBUG] filter_sites_by_country - Sede {site.get('site_id')}: timezone={site_timezone}, país={site_country}, coincide={site_country == country}")
        
        if site_country == country:
            filtered.append(site)
    
    print(f"[DEBUG] filter_sites_by_country - Resultado: {len(filtered)} sedes filtradas para {country}")
    return filtered


def filter_polygons_by_country(
    polygons: List[Dict], 
    sites: List[Dict], 
    country: Country
) -> List[Dict]:
    """
    Filtra polígonos por país basado en el campo 'country' del polígono o la sede asociada.
    
    Args:
        polygons: Lista de polígonos
        sites: Lista de sedes (para obtener el país de cada sede si el polígono no tiene country)
        country: País a filtrar ('colombia', 'usa', 'spain')
    
    Returns:
        Lista de polígonos filtrados
    """
    # Crear un mapa de site_id -> país (para polígonos sin campo country)
    site_country_map = {}
    for site in sites:
        site_id = site.get('site_id')
        if site_id:
            site_timezone = site.get('time_zone')
            site_country = get_country_from_timezone(site_timezone)
            if site_country:
                site_country_map[site_id] = site_country
    
    # Filtrar polígonos
    filtered = []
    for polygon in polygons:
        # Priorizar el campo 'country' del polígono
        polygon_country = polygon.get('country')
        
        # Si no tiene campo country, usar la sede asociada
        if not polygon_country:
            site_id = polygon.get('site_id')
            if site_id:
                polygon_country = site_country_map.get(site_id)
        
        # Solo incluir polígonos que tienen un país asignado y coincide
        if polygon_country and polygon_country == country:
            filtered.append(polygon)
    
    return filtered


def filter_picking_points_by_country(
    picking_points: List[Dict],
    sites: List[Dict],
    country: Country
) -> List[Dict]:
    """
    Filtra picking points por país basado en la sede asociada.
    
    Args:
        picking_points: Lista de picking points
        sites: Lista de sedes (para obtener el país de cada sede)
        country: País a filtrar ('colombia', 'usa', 'spain')
    
    Returns:
        Lista de picking points filtrados
    """
    
    # Crear un mapa de site_id -> país
    site_country_map = {}
    for site in sites:
        site_id = site.get('site_id')
        if site_id:
            site_timezone = site.get('time_zone')
            site_country = get_country_from_timezone(site_timezone)
            if site_country:
                site_country_map[site_id] = site_country
    
    # Filtrar picking points
    filtered = []
    for pp in picking_points:
        site_id = pp.get('site_id')
        if not site_id:
            continue
        
        pp_country = site_country_map.get(site_id)
        if pp_country == country:
            filtered.append(pp)
    
    return filtered


def filter_orders_by_country(
    orders: List[Dict],
    sites: List[Dict],
    country: Country
) -> List[Dict]:
    """
    Filtra órdenes por país basado en el campo 'country' de la orden o la ciudad.
    Si la orden tiene campo 'country', se usa directamente. Si no, se mapea la ciudad a país a través de las sedes.
    
    Args:
        orders: Lista de órdenes
        sites: Lista de sedes (para obtener ciudades por país si la orden no tiene campo country)
        country: País a filtrar ('colombia', 'usa', 'spain')
    
    Returns:
        Lista de órdenes filtradas
    """
    
    # Obtener ciudades del país seleccionado (para órdenes sin campo country)
    country_sites = filter_sites_by_country(sites, country)
    country_cities = set()
    for site in country_sites:
        city_name = site.get('city_name')
        if city_name:
            country_cities.add(city_name.lower())  # Normalizar a minúsculas para comparación
    
    # Filtrar órdenes
    filtered = []
    for order in orders:
        # Priorizar el campo 'country' de la orden si existe
        order_country = order.get('country')
        if order_country:
            # Normalizar el país de la orden para comparación
            order_country_normalized = order_country.lower().strip()
            if order_country_normalized == country:
                filtered.append(order)
                continue
        
        # Si no tiene campo country, usar el mapeo por ciudad (fallback)
        order_city = order.get('city')
        if order_city:
            order_city_normalized = order_city.lower().strip()
            if order_city_normalized in country_cities:
                filtered.append(order)
    
    return filtered
