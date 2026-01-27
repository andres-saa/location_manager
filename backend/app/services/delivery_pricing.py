"""
Servicio para calcular tarifas de entrega por kilómetro
USA y España siempre usan tarifa calculada (nunca Rappi Cargo).
Colombia solo usa tarifa calculada cuando el modo es 'calculated' (si es 'cargo', usa Rappi Cargo).
"""
from typing import Optional, Dict, Any
from app.utils.geometry import calculate_distance
from app.storage.json_storage import get_site_tariff
from app.utils.country_filter import get_country_from_timezone as get_country_from_tz


def calculate_delivery_price(
    distance_km: float,
    site: Dict,
    price_per_km: Optional[float] = None,
    min_fee: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calcula el precio de entrega basado en la distancia y la tarifa de la sede.
    USA y España siempre usan tarifa calculada. Colombia solo cuando el modo es 'calculated'.
    
    Args:
        distance_km: Distancia en kilómetros
        site: Diccionario con información de la sede (debe incluir time_zone, min_delivery_fee, price_per_km)
        price_per_km: Precio por kilómetro (opcional, se toma de site si no se proporciona)
        min_fee: Tarifa mínima (opcional, se toma de site si no se proporciona)
    
    Returns:
        Dict con 'price', 'distance_km', 'price_per_km', 'min_fee', 'max_fee', 'country', 'uses_rappi'
    """
    country = get_country_from_tz(site.get('time_zone')) or 'unknown'
    
    # USA y España siempre usan tarifa calculada
    # Colombia solo usa tarifa calculada cuando el modo es 'calculated' (se valida en check.py antes de llamar)
    if country not in ['usa', 'spain', 'colombia']:
        return {
            'price': None,
            'distance_km': distance_km,
            'price_per_km': None,
            'min_fee': None,
            'max_fee': None,
            'country': country,
            'uses_rappi': True
        }
    
    # Obtener tarifas personalizadas de la sede si existen
    site_tariff = get_site_tariff(site.get('site_id'))
    
    # Priorizar: parámetros > tarifa personalizada > valores de la sede > valores por defecto
    tariff_mode = site_tariff.get('tariff_mode', 'fixed') if site_tariff else 'fixed'
    site_price_per_km = price_per_km or (site_tariff.get('price_per_km') if site_tariff else None) or site.get('price_per_km')
    site_min_fee = min_fee or (site_tariff.get('min_fee') if site_tariff else None) or site.get('min_delivery_fee')
    site_max_fee = site_tariff.get('max_fee') if site_tariff else None
    
    # Campos para modo surcharge
    base_distance_km = site_tariff.get('base_distance_km') if site_tariff else None
    surcharge_per_km = site_tariff.get('surcharge_per_km') if site_tariff else None
    
    # Valores por defecto si no están configurados
    if site_price_per_km is None:
        if country == 'usa':
            site_price_per_km = 2.0  # USD por km
        elif country == 'spain':
            site_price_per_km = 1.5  # EUR por km
        else:  # colombia
            site_price_per_km = 2000.0  # COP por km
    
    if site_min_fee is None:
        if country == 'usa':
            site_min_fee = 5.0  # USD
        elif country == 'spain':
            site_min_fee = 3.0  # EUR
        else:  # colombia
            site_min_fee = 5000.0  # COP
    
    # Calcular precio según el modo de tarifa
    if tariff_mode == 'surcharge' and base_distance_km is not None and surcharge_per_km is not None:
        # Modo con recargo: precio base hasta base_distance_km, luego recargo adicional
        if distance_km <= base_distance_km:
            # Distancia dentro del rango base: precio fijo
            calculated_price = distance_km * site_price_per_km
        else:
            # Distancia excede el rango base: precio base + recargo por km adicional
            base_price = base_distance_km * site_price_per_km
            additional_km = distance_km - base_distance_km
            surcharge = additional_km * surcharge_per_km
            calculated_price = base_price + surcharge
    else:
        # Modo fijo: precio fijo por kilómetro
        calculated_price = distance_km * site_price_per_km
    
    # Aplicar tarifa mínima
    final_price = max(calculated_price, site_min_fee)
    
    # Aplicar tarifa máxima si está configurada
    if site_max_fee is not None and final_price > site_max_fee:
        final_price = site_max_fee
    
    return {
        'price': round(final_price, 2),
        'distance_km': round(distance_km, 2),
        'price_per_km': site_price_per_km,
        'min_fee': site_min_fee,
        'max_fee': site_max_fee,
        'country': country,
        'uses_rappi': False
    }


def calculate_delivery_price_from_coordinates(
    client_lat: float,
    client_lng: float,
    site: Dict
) -> Optional[Dict[str, Any]]:
    """
    Calcula el precio de entrega desde las coordenadas del cliente hasta la sede.
    
    Args:
        client_lat: Latitud del cliente
        client_lng: Longitud del cliente
        site: Diccionario con información de la sede (debe incluir location, time_zone, etc.)
    
    Returns:
        Dict con información de precio o None si no se puede calcular
    """
    site_location = site.get('location')
    if not site_location or not isinstance(site_location, list) or len(site_location) < 2:
        return None
    
    site_lat = site_location[0]
    site_lng = site_location[1]
    
    # Calcular distancia
    distance_km = calculate_distance(client_lat, client_lng, site_lat, site_lng)
    
    # Calcular precio
    return calculate_delivery_price(distance_km, site)
