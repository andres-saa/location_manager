from fastapi import APIRouter, HTTPException, status
from datetime import datetime

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.storage.json_storage import get_all_polygons, get_picking_point_by_site_id, get_app_config
from app.schemas.check import AddressCheck, CheckAddressResponse, PolygonMatch, RappiValidationResponse, DeliveryPricingResponse
from app.schemas.polygon import PolygonResponse
from app.utils.geometry import point_in_polygon, calculate_polygon_center, calculate_distance
from app.services.sites import get_available_sites, get_site_by_id
from app.services.geocoding import geocode_address
from app.services.rappi_validation import validate_order_with_rappi
from app.services.delivery_pricing import calculate_delivery_price_from_coordinates
from app.utils.country_filter import get_country_from_timezone
from app.core.config import settings

router = APIRouter(prefix="/check", tags=["Check"])

def _dict_to_polygon_response(polygon_dict: dict) -> PolygonResponse:
    """Convierte un diccionario a PolygonResponse"""
    return PolygonResponse(
        id=polygon_dict['id'],
        name=polygon_dict['name'],
        description=polygon_dict.get('description'),
        coordinates=polygon_dict['coordinates'],
        color=polygon_dict.get('color', '#FF0000'),
        site_id=polygon_dict.get('site_id'),
        country=polygon_dict.get('country'),
        created_at=datetime.fromisoformat(polygon_dict['created_at']) if polygon_dict.get('created_at') else datetime.now(),
        updated_at=datetime.fromisoformat(polygon_dict['updated_at']) if polygon_dict.get('updated_at') else None
    )

@router.post("/address", response_model=CheckAddressResponse)
async def check_address(address_check: AddressCheck):
    """
    Verifica en qué polígono/sede cae una dirección.
    Primero geocodifica la dirección a coordenadas, luego verifica en qué polígonos cae.
    Si la dirección cae en múltiples polígonos, retorna solo el más central (el cuyo centro esté más cerca de la coordenada).
    Retorna el polígono que contiene el punto, incluyendo la información de la sede asociada.
    """
    # Geocodificar la dirección
    api_key = settings.google_maps_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Maps API Key no configurada. Configure GOOGLE_MAPS_API_KEY en las variables de entorno."
        )
    
    coordinates = await geocode_address(
        address_check.address, 
        api_key,
        city=address_check.city,
        country=address_check.country or "Colombia"
    )
    
    if not coordinates:
        return CheckAddressResponse(
            address=address_check.address,
            formatted_address=None,
            latitude=None,
            longitude=None,
            geocoded=False,
            is_inside_any=False,
            matching_polygons=[]
        )
    
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']
    formatted_address = coordinates.get('formatted_address', address_check.address)
    
    # Obtener configuración de la aplicación
    app_config = get_app_config()
    validation_mode = app_config.get('validation_mode', 'polygons')
    
    # Obtener sedes disponibles
    sites = await get_available_sites()
    
    matching_polygons = []
    
    if validation_mode == 'polygons':
        # Modo polígonos: buscar polígonos que contengan el punto
        # Filtrar polígonos por país basado en el campo 'country' o la sede asociada
        from app.utils.country_filter import filter_polygons_by_country
        
        all_polygons = get_all_polygons()
        
        # Determinar el país desde el parámetro country (puede venir como "Colombia", "Estados Unidos", etc.)
        country_param = address_check.country or "Colombia"
        country_code = None
        if "Colombia" in country_param or "colombia" in country_param.lower():
            country_code = 'colombia'
        elif "Estados Unidos" in country_param or "USA" in country_param or "usa" in country_param.lower():
            country_code = 'usa'
        elif "España" in country_param or "Spain" in country_param or "spain" in country_param.lower():
            country_code = 'spain'
        
        # Filtrar polígonos por país si se especificó
        if country_code:
            polygons = filter_polygons_by_country(all_polygons, sites, country_code)
        else:
            polygons = all_polygons
        
        # Encontrar todos los polígonos que contienen el punto
        for polygon_dict in polygons:
            is_inside = point_in_polygon(
                latitude,
                longitude,
                polygon_dict['coordinates']
            )
            
            if is_inside:
                # Obtener información de la sede si está asociada
                site = None
                site_id = polygon_dict.get('site_id')
                if site_id:
                    site = get_site_by_id(sites, site_id)
                
                matching_polygons.append(
                    PolygonMatch(
                        polygon=_dict_to_polygon_response(polygon_dict),
                        is_inside=True,
                        site=site
                    )
                )
        
        # Si hay múltiples polígonos, seleccionar el más central
        if len(matching_polygons) > 1:
            best_match = None
            min_distance = float('inf')
            
            for match in matching_polygons:
                polygon_coords = match.polygon.coordinates
                center_lat, center_lng = calculate_polygon_center(polygon_coords)
                distance = calculate_distance(latitude, longitude, center_lat, center_lng)
                
                if distance < min_distance:
                    min_distance = distance
                    best_match = match
            
            matching_polygons = [best_match] if best_match else []
    
    elif validation_mode == 'nearest_site':
        # Modo sede más cercana: encontrar la sede más cercana a la dirección (funciona para todos los países)
        nearest_site = None
        min_distance = float('inf')
        
        for site in sites:
            site_location = site.get('location')
            if site_location and isinstance(site_location, list) and len(site_location) == 2:
                site_lat = site_location[0]
                site_lng = site_location[1]
                distance = calculate_distance(latitude, longitude, site_lat, site_lng)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_site = site
        
        # Si encontramos una sede cercana, buscar si tiene un polígono asociado
        if nearest_site:
            site_id = nearest_site.get('site_id')
            polygons = get_all_polygons()
            
            # Buscar polígonos asociados a esta sede
            associated_polygon = None
            for polygon_dict in polygons:
                if polygon_dict.get('site_id') == site_id:
                    associated_polygon = polygon_dict
                    break
            
            if associated_polygon:
                # Verificar si el punto está dentro del polígono
                is_inside = point_in_polygon(
                    latitude,
                    longitude,
                    associated_polygon['coordinates']
                )
                
                matching_polygons.append(
                    PolygonMatch(
                        polygon=_dict_to_polygon_response(associated_polygon),
                        is_inside=is_inside,
                        site=nearest_site
                    )
                )
            else:
                # Si no hay polígono asociado, crear un match con un polígono mínimo centrado en la sede
                from app.schemas.polygon import PolygonResponse
                # Crear un pequeño polígono alrededor de la sede para visualización
                site_location = nearest_site.get('location', [latitude, longitude])
                site_lat = site_location[0] if len(site_location) > 0 else latitude
                site_lng = site_location[1] if len(site_location) > 1 else longitude
                # Polígono pequeño de ~100m alrededor de la sede
                offset = 0.001  # ~100m
                virtual_coords = [
                    [site_lat + offset, site_lng + offset],
                    [site_lat + offset, site_lng - offset],
                    [site_lat - offset, site_lng - offset],
                    [site_lat - offset, site_lng + offset],
                    [site_lat + offset, site_lng + offset]
                ]
                
                matching_polygons.append(
                    PolygonMatch(
                        polygon=PolygonResponse(
                            id=0,
                            name=f"Sede más cercana: {nearest_site.get('site_name', 'N/A')}",
                            description="Sede seleccionada automáticamente por proximidad",
                            coordinates=virtual_coords,
                            color='#FFA500',
                            site_id=site_id,
                            created_at=datetime.now(),
                            updated_at=None
                        ),
                        is_inside=True,
                        site=nearest_site
                    )
                )
    
    # Inicializar ambos objetos como None (se establecerán según el modo de entrega)
    rappi_validation = None
    delivery_pricing = None
    exceeds_max_distance = None
    distance_to_site_km = None
    
    # Obtener distancia máxima configurada (solo se aplica para tarifa calculada, no para Rappi Cargo)
    max_delivery_distance_km = app_config.get('max_delivery_distance_km')
    is_inside_polygon = len(matching_polygons) > 0
    
    if latitude and longitude:
        # Buscar la sede más cercana o la del polígono
        site = None
        if is_inside_polygon:
            # Usar el primer polígono encontrado (o el más central si hay múltiples)
            polygon_match = matching_polygons[0]
            site = polygon_match.site
        else:
            # Si no está en ningún polígono, buscar la sede más cercana
            sites = await get_available_sites()
            if sites:
                min_distance = float('inf')
                for s in sites:
                    site_location = s.get('location')
                    if site_location and isinstance(site_location, list) and len(site_location) >= 2:
                        site_lat = site_location[0]
                        site_lng = site_location[1]
                        dist = calculate_distance(latitude, longitude, site_lat, site_lng)
                        if dist < min_distance:
                            min_distance = dist
                            site = s
                if site:
                    distance_to_site_km = round(min_distance, 2)
        
        # Determinar el país y modo de entrega para saber si aplicar distancia máxima
        country = None
        uses_calculated_tariff = False
        
        if site:
            country = get_country_from_timezone(site.get('time_zone'))
            if country == 'colombia':
                colombia_delivery_mode = app_config.get('colombia_delivery_mode', 'cargo')
                # Solo aplicar distancia máxima si usa tarifa calculada (no Rappi Cargo)
                uses_calculated_tariff = (colombia_delivery_mode == 'calculated')
            elif country in ['usa', 'spain']:
                # USA y España siempre usan tarifa calculada
                uses_calculated_tariff = True
        
        # Validar distancia máxima solo si:
        # 1. NO está dentro de un polígono
        # 2. Usa tarifa calculada (no Rappi Cargo)
        # 3. Hay distancia máxima configurada
        if (max_delivery_distance_km is not None and 
            distance_to_site_km is not None and 
            not is_inside_polygon and 
            uses_calculated_tariff):
            exceeds_max_distance = distance_to_site_km > max_delivery_distance_km
        
        # Calcular tarifas o validar con Rappi solo si está dentro de un polígono
        if is_inside_polygon and site:
            if country == 'colombia':
                # Colombia: usar Rappi Cargo o tarifa calculada según configuración
                colombia_delivery_mode = app_config.get('colombia_delivery_mode', 'cargo')
                
                if colombia_delivery_mode == 'cargo':
                    # Usar Rappi Cargo (la distancia máxima la determina Rappi)
                    external_picking_point_id = site.get('picking_point_external_id')
                    # Si no está en la sede enriquecida, buscar directamente (fallback)
                    if not external_picking_point_id and site.get('site_id'):
                        site_id = site['site_id']
                        picking_point = get_picking_point_by_site_id(site_id)
                        if picking_point and picking_point.get('external_id'):
                            external_picking_point_id = picking_point['external_id']
                    
                    # Solo validar con Rappi si tenemos un external_id válido
                    if external_picking_point_id:
                        rappi_result = await validate_order_with_rappi(
                            address=formatted_address or address_check.address,
                            lat=latitude,
                            lng=longitude,
                            city=address_check.city or "Bogota",
                            external_picking_point_id=external_picking_point_id
                        )
                        if rappi_result:
                            # Establecer rappi_validation con los datos reales
                            rappi_validation = RappiValidationResponse(**rappi_result)
                    # delivery_pricing permanece None para Rappi Cargo
                else:
                    # Usar tarifa calculada (como USA/España)
                    pricing_result = calculate_delivery_price_from_coordinates(
                        latitude,
                        longitude,
                        site
                    )
                    if pricing_result:
                        # Establecer delivery_pricing con los datos reales
                        delivery_pricing = DeliveryPricingResponse(**pricing_result)
                    # rappi_validation permanece None para tarifa calculada
            
            elif country in ['usa', 'spain']:
                # USA y España: siempre calcular tarifas por kilómetro
                pricing_result = calculate_delivery_price_from_coordinates(
                    latitude,
                    longitude,
                    site
                )
                if pricing_result:
                    # Establecer delivery_pricing con los datos reales
                    delivery_pricing = DeliveryPricingResponse(**pricing_result)
                # rappi_validation permanece None para USA/España
    
    return CheckAddressResponse(
        address=address_check.address,
        formatted_address=formatted_address,
        latitude=latitude,
        longitude=longitude,
        geocoded=True,
        is_inside_any=is_inside_polygon,
        matching_polygons=matching_polygons,
        rappi_validation=rappi_validation,
        delivery_pricing=delivery_pricing,
        exceeds_max_distance=exceeds_max_distance,
        distance_to_site_km=distance_to_site_km
    )
