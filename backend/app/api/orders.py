"""
Endpoints para gestionar órdenes/pedidos
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime

import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.storage.json_storage import create_order, get_all_orders, get_orders_by_date_range
from app.storage.json_storage import get_all_polygons
from app.utils.geometry import point_in_polygon
from app.utils.country_filter import filter_orders_by_country, Country
from app.services.sites import get_available_sites

router = APIRouter(prefix="/orders", tags=["Orders"])


def _dict_to_order_response(order_dict: dict) -> OrderResponse:
    """Convierte un diccionario a OrderResponse"""
    return OrderResponse(
        id=order_dict['id'],
        latitude=order_dict['latitude'],
        longitude=order_dict['longitude'],
        address=order_dict['address'],
        formatted_address=order_dict.get('formatted_address'),  # Dirección formateada de Rappi Cargo
        first_name=order_dict['first_name'],
        last_name=order_dict['last_name'],
        phone=order_dict['phone'],
        email=order_dict['email'],
        complement=order_dict.get('complement'),
        city=order_dict.get('city'),
        country=order_dict.get('country'),
        comments=order_dict.get('comments'),
        order_date=order_dict.get('order_date', order_dict.get('created_at', '')),
        created_at=order_dict.get('created_at', '')
    )


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(order: OrderCreate):
    """
    Registra una nueva orden/pedido desde la tienda virtual.
    """
    order_data = order.model_dump()
    
    # Si no se proporciona order_date, usar la fecha actual
    if not order_data.get('order_date'):
        order_data['order_date'] = datetime.now().isoformat()
    else:
        # Si viene como datetime, convertirlo a string
        if isinstance(order_data['order_date'], datetime):
            order_data['order_date'] = order_data['order_date'].isoformat()
    
    created_order = create_order(order_data)
    return _dict_to_order_response(created_order)


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    start_date: Optional[str] = Query(None, alias="start_date", description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, alias="end_date", description="Fecha de fin (YYYY-MM-DD)"),
    cities: Optional[List[str]] = Query(None, description="Lista de ciudades/ubicaciones para filtrar (puede enviarse múltiples veces: cities=valor1&cities=valor2)"),
    country: Optional[str] = Query(None, description="Filtrar por país: 'colombia', 'usa', 'spain'")
):
    """
    Obtiene todas las órdenes, opcionalmente filtradas por rango de fechas, ciudades y/o país.
    Incluye estadísticas de órdenes por zona/polígono.
    
    Args:
        start_date: Fecha de inicio para filtrar (YYYY-MM-DD)
        end_date: Fecha de fin para filtrar (YYYY-MM-DD)
        cities: Lista de ciudades/ubicaciones para filtrar
        country: País para filtrar las órdenes ('colombia', 'usa', 'spain')
    """
    # Verificar si hay algún filtro activo (fechas o ciudades no vacías)
    has_date_filter = start_date or end_date
    has_city_filter = cities and len(cities) > 0
    
    print(f"[DEBUG] get_orders - Filtros recibidos: start_date={start_date}, end_date={end_date}, cities={cities} (tipo: {type(cities)}), country={country}")
    print(f"[DEBUG] get_orders - has_date_filter={has_date_filter}, has_city_filter={has_city_filter}")
    if cities:
        print(f"[DEBUG] get_orders - cities es: {cities}, len={len(cities) if cities else 0}, bool={bool(cities)}")
    
    # Si se especifica país, primero filtrar por país para reducir el conjunto de datos
    # Luego aplicar filtros de fecha y ciudades
    if country:
        # Obtener todas las órdenes primero
        all_orders = get_all_orders()
        print(f"[DEBUG] get_orders - Total de órdenes antes de filtrar: {len(all_orders)}")
        
        # Filtrar por país primero (usando campo country si está disponible, o mapeo por ciudades)
        sites = await get_available_sites()
        orders = filter_orders_by_country(all_orders, sites, country)
        print(f"[DEBUG] get_orders - Órdenes después de filtrar por país '{country}': {len(orders)}")
        
        # SIEMPRE aplicar filtros de fecha y ciudades si se especifican (incluso si solo hay ciudades sin fechas)
        print(f"[DEBUG] get_orders - Verificando si aplicar filtros adicionales: has_date_filter={has_date_filter}, has_city_filter={has_city_filter}")
        if has_date_filter or has_city_filter:
            # Crear una lista temporal para aplicar los filtros adicionales
            filtered_by_country = orders
            orders = []
            
            print(f"[DEBUG] get_orders - ✅ Aplicando filtros adicionales sobre {len(filtered_by_country)} órdenes")
            print(f"[DEBUG] get_orders - Filtro de ciudades activo: {has_city_filter}, ciudades: {cities}")
            
            for order in filtered_by_country:
                order_city = order.get('city', '')
                if order_city:
                    order_city = order_city.strip()
                    order_city_lower = order_city.lower()
                else:
                    order_city_lower = ''
                
                # Filtrar por ciudades si se especifican (OBLIGATORIO si se proporciona)
                if has_city_filter:
                    # Normalizar ciudades del filtro (manejar acentos y caracteres especiales)
                    import unicodedata
                    normalized_filter_cities = []
                    for city in cities:
                        if city:
                            # Normalizar: quitar acentos y convertir a minúsculas
                            city_normalized = unicodedata.normalize('NFD', city.strip().lower())
                            city_normalized = ''.join(c for c in city_normalized if unicodedata.category(c) != 'Mn')
                            normalized_filter_cities.append(city_normalized)
                    
                    # Normalizar también la ciudad de la orden
                    order_city_normalized = ''
                    if order_city_lower:
                        order_city_normalized = unicodedata.normalize('NFD', order_city_lower)
                        order_city_normalized = ''.join(c for c in order_city_normalized if unicodedata.category(c) != 'Mn')
                    
                    print(f"[DEBUG] get_orders - Comparando: orden_city='{order_city}' -> normalized='{order_city_normalized}' vs filter_cities={normalized_filter_cities}")
                    
                    city_matches = any(
                        filter_city == order_city_normalized 
                        for filter_city in normalized_filter_cities
                    )
                    
                    if not city_matches:
                        print(f"[DEBUG] get_orders - Orden {order.get('id')} EXCLUIDA: ciudad '{order_city}' (normalized: '{order_city_normalized}') no coincide con ciudades filtradas {normalized_filter_cities}")
                        continue  # Excluir si no coincide con ninguna ciudad filtrada
                    else:
                        print(f"[DEBUG] get_orders - Orden {order.get('id')} PASA filtro de ciudad: '{order_city}' coincide con {normalized_filter_cities}")
                
                # Filtrar por fecha si se especifican
                if has_date_filter:
                    order_date_str = order.get('order_date', order.get('created_at', ''))
                    
                    if not order_date_str:
                        continue
                    else:
                        order_date_normalized = order_date_str.split('T')[0] if 'T' in order_date_str else order_date_str.split(' ')[0]
                        
                        if start_date:
                            start_normalized = start_date.split('T')[0] if 'T' in start_date else start_date.split(' ')[0]
                            if order_date_normalized < start_normalized:
                                continue
                        
                        if end_date:
                            end_normalized = end_date.split('T')[0] if 'T' in end_date else end_date.split(' ')[0]
                            if order_date_normalized > end_normalized:
                                continue
                
                # Si pasa todos los filtros, incluir la orden
                orders.append(order)
            
            print(f"[DEBUG] get_orders - Órdenes después de aplicar filtros adicionales: {len(orders)}")
        else:
            print(f"[DEBUG] get_orders - ⚠️ NO se aplicarán filtros adicionales (solo país), devolviendo {len(orders)} órdenes")
    else:
        # Si no hay filtro de país, usar la función existente
        if has_date_filter or has_city_filter:
            orders = get_orders_by_date_range(start_date, end_date, cities if has_city_filter else None)
        else:
            orders = get_all_orders()
    
    # Convertir a OrderResponse
    order_responses = [_dict_to_order_response(order) for order in orders]
    
    # Calcular estadísticas por zona/polígono (solo para las órdenes filtradas)
    polygons = get_all_polygons()
    zone_stats = {}
    
    for order in orders:
        lat = order.get('latitude')
        lng = order.get('longitude')
        
        if not lat or not lng:
            continue
        
        # Buscar en qué polígonos cae esta orden
        found_zone = None
        for polygon in polygons:
            if point_in_polygon(lat, lng, polygon.get('coordinates', [])):
                polygon_name = polygon.get('name', f"Polígono {polygon.get('id')}")
                found_zone = polygon_name
                break
        
        # Si no está en ningún polígono, usar "Sin zona"
        if not found_zone:
            found_zone = "Sin zona"
        
        # Incrementar contador
        if found_zone not in zone_stats:
            zone_stats[found_zone] = 0
        zone_stats[found_zone] += 1
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses),
        zone_stats=zone_stats
    )
