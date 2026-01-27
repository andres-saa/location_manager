"""
Sistema de almacenamiento basado en archivos JSON
"""
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

import sys

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Directorio para almacenar los archivos JSON
DATA_DIR = Path(backend_path) / "data"
POLYGONS_FILE = DATA_DIR / "polygons.json"
LOCATIONS_FILE = DATA_DIR / "locations.json"
SITES_CACHE_FILE = DATA_DIR / "sites_cache.json"
PICKING_POINTS_FILE = DATA_DIR / "picking_points.json"
APP_CONFIG_FILE = DATA_DIR / "app_config.json"
ORDERS_FILE = DATA_DIR / "orders.json"
SITE_TARIFFS_FILE = DATA_DIR / "site_tariffs.json"

# Asegurar que el directorio existe
DATA_DIR.mkdir(exist_ok=True)


def _load_json(file_path: Path, default: Any = None) -> Any:
    """Carga un archivo JSON, retorna el valor por defecto si no existe"""
    if default is None:
        default = []
    
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error cargando {file_path}: {e}")
        return default


def _save_json(file_path: Path, data: Any) -> None:
    """Guarda datos en un archivo JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error guardando {file_path}: {e}")
        raise


def _get_next_id(items: List[Dict]) -> int:
    """Obtiene el siguiente ID disponible"""
    if not items:
        return 1
    max_id = max(item.get('id', 0) for item in items)
    return max_id + 1


def _format_datetime(dt: Optional[datetime] = None) -> str:
    """Formatea datetime a string ISO"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parsea string ISO a datetime"""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None


# ==================== POLYGONS ====================

def get_all_polygons() -> List[Dict]:
    """Obtiene todos los polígonos"""
    return _load_json(POLYGONS_FILE, [])


def get_polygon(polygon_id: int) -> Optional[Dict]:
    """Obtiene un polígono por ID"""
    polygons = get_all_polygons()
    for polygon in polygons:
        if polygon.get('id') == polygon_id:
            return polygon
    return None


def get_polygon_by_site_id(site_id: int, exclude_polygon_id: Optional[int] = None) -> Optional[Dict]:
    """Obtiene un polígono por site_id, excluyendo un polígono específico si se proporciona"""
    polygons = get_all_polygons()
    for polygon in polygons:
        if polygon.get('site_id') == site_id:
            # Si se especifica un polígono a excluir, saltarlo
            if exclude_polygon_id is not None and polygon.get('id') == exclude_polygon_id:
                continue
            return polygon
    return None


def create_polygon(polygon_data: Dict) -> Dict:
    """Crea un nuevo polígono"""
    polygons = get_all_polygons()
    
    new_polygon = {
        'id': _get_next_id(polygons),
        'name': polygon_data['name'],
        'description': polygon_data.get('description'),
        'coordinates': polygon_data['coordinates'],
        'color': polygon_data.get('color', '#FF0000'),
        'site_id': polygon_data.get('site_id'),
        'country': polygon_data.get('country'),
        'created_at': _format_datetime(),
        'updated_at': None
    }
    
    polygons.append(new_polygon)
    _save_json(POLYGONS_FILE, polygons)
    return new_polygon


def update_polygon(polygon_id: int, polygon_data: Dict) -> Optional[Dict]:
    """Actualiza un polígono"""
    polygons = get_all_polygons()
    
    for i, polygon in enumerate(polygons):
        if polygon.get('id') == polygon_id:
            # Actualizar solo los campos proporcionados
            for key, value in polygon_data.items():
                if value is not None:
                    polygon[key] = value
            
            polygon['updated_at'] = _format_datetime()
            polygons[i] = polygon
            _save_json(POLYGONS_FILE, polygons)
            return polygon
    
    return None


def delete_polygon(polygon_id: int) -> bool:
    """Elimina un polígono"""
    polygons = get_all_polygons()
    original_count = len(polygons)
    
    polygons = [p for p in polygons if p.get('id') != polygon_id]
    
    if len(polygons) < original_count:
        _save_json(POLYGONS_FILE, polygons)
        return True
    return False


# ==================== LOCATIONS ====================

def get_all_locations() -> List[Dict]:
    """Obtiene todas las locaciones"""
    return _load_json(LOCATIONS_FILE, [])


def get_location(location_id: int) -> Optional[Dict]:
    """Obtiene una locación por ID"""
    locations = get_all_locations()
    for location in locations:
        if location.get('id') == location_id:
            return location
    return None


def get_locations_by_polygon(polygon_id: Optional[int] = None) -> List[Dict]:
    """Obtiene locaciones, opcionalmente filtradas por polígono"""
    locations = get_all_locations()
    if polygon_id is not None:
        locations = [loc for loc in locations if loc.get('polygon_id') == polygon_id]
    return locations


def create_location(location_data: Dict) -> Dict:
    """Crea una nueva locación"""
    locations = get_all_locations()
    
    # Verificar que el polígono existe si se especifica
    if location_data.get('polygon_id'):
        polygon = get_polygon(location_data['polygon_id'])
        if not polygon:
            raise ValueError(f"Polígono con ID {location_data['polygon_id']} no encontrado")
    
    new_location = {
        'id': _get_next_id(locations),
        'name': location_data['name'],
        'description': location_data.get('description'),
        'latitude': location_data['latitude'],
        'longitude': location_data['longitude'],
        'address': location_data.get('address'),
        'polygon_id': location_data.get('polygon_id'),
        'created_at': _format_datetime(),
        'updated_at': None
    }
    
    locations.append(new_location)
    _save_json(LOCATIONS_FILE, locations)
    return new_location


def update_location(location_id: int, location_data: Dict) -> Optional[Dict]:
    """Actualiza una locación"""
    locations = get_all_locations()
    
    # Verificar que el polígono existe si se está actualizando
    if location_data.get('polygon_id') is not None:
        polygon = get_polygon(location_data['polygon_id'])
        if not polygon:
            raise ValueError(f"Polígono con ID {location_data['polygon_id']} no encontrado")
    
    for i, location in enumerate(locations):
        if location.get('id') == location_id:
            # Actualizar solo los campos proporcionados
            for key, value in location_data.items():
                if value is not None:
                    location[key] = value
            
            location['updated_at'] = _format_datetime()
            locations[i] = location
            _save_json(LOCATIONS_FILE, locations)
            return location
    
    return None


def delete_location(location_id: int) -> bool:
    """Elimina una locación"""
    locations = get_all_locations()
    original_count = len(locations)
    
    locations = [loc for loc in locations if loc.get('id') != location_id]
    
    if len(locations) < original_count:
        _save_json(LOCATIONS_FILE, locations)
        return True
    return False


# ==================== SITES CACHE ====================

def save_sites_cache(sites: List[Dict]) -> None:
    """Guarda el caché de sedes con timestamp"""
    cache_data = {
        'sites': sites,
        'last_updated': _format_datetime()
    }
    _save_json(SITES_CACHE_FILE, cache_data)


def get_sites_cache() -> Optional[Dict]:
    """Obtiene el caché de sedes"""
    return _load_json(SITES_CACHE_FILE, None)


def is_cache_valid(max_age_seconds: int = 180) -> bool:
    """
    Verifica si el caché es válido (no ha expirado)
    
    Args:
        max_age_seconds: Edad máxima del caché en segundos (default: 180 = 3 minutos)
    """
    cache_data = get_sites_cache()
    if not cache_data or not cache_data.get('last_updated'):
        return False
    
    try:
        last_updated = _parse_datetime(cache_data.get('last_updated'))
        if not last_updated:
            return False
        
        age_seconds = (datetime.now() - last_updated).total_seconds()
        return age_seconds < max_age_seconds
    except Exception:
        return False


# ==================== SITES CACHE ====================

def get_sites_cache() -> Optional[Dict]:
    """Obtiene el caché de sedes con su timestamp"""
    cache_data = _load_json(SITES_CACHE_FILE, None)
    return cache_data


def save_sites_cache(sites: List[Dict]) -> None:
    """Guarda el caché de sedes con timestamp"""
    cache_data = {
        'sites': sites,
        'last_updated': _format_datetime(),
        'timestamp': datetime.now().timestamp()
    }
    _save_json(SITES_CACHE_FILE, cache_data)


def is_cache_valid(max_age_seconds: int = 180) -> bool:
    """
    Verifica si el caché es válido (no ha expirado)
    
    Args:
        max_age_seconds: tiempo máximo de validez en segundos (default: 180 = 3 minutos)
    """
    cache_data = get_sites_cache()
    if not cache_data:
        return False
    
    timestamp = cache_data.get('timestamp')
    if not timestamp:
        # Si no hay timestamp, intentar usar last_updated
        last_updated_str = cache_data.get('last_updated')
        if last_updated_str:
            last_updated = _parse_datetime(last_updated_str)
            if last_updated:
                age_seconds = (datetime.now() - last_updated).total_seconds()
                return age_seconds < max_age_seconds
        return False
    
    current_time = datetime.now().timestamp()
    age = current_time - timestamp
    
    return age < max_age_seconds


# ==================== PICKING POINTS ====================

def get_all_picking_points() -> List[Dict]:
    """Obtiene todos los picking points asociados a sedes"""
    return _load_json(PICKING_POINTS_FILE, [])


def get_picking_point(picking_point_id: int) -> Optional[Dict]:
    """Obtiene un picking point por ID"""
    picking_points = get_all_picking_points()
    for pp in picking_points:
        if pp.get('id') == picking_point_id:
            return pp
    return None


def get_picking_points_by_site_id(site_id: int) -> List[Dict]:
    """Obtiene todos los picking points asociados a una sede"""
    picking_points = get_all_picking_points()
    return [pp for pp in picking_points if pp.get('site_id') == site_id]


def get_picking_point_by_site_id(site_id: int) -> Optional[Dict]:
    """Obtiene el picking point asociado a una sede (relación 1 a 1)"""
    picking_points = get_all_picking_points()
    for pp in picking_points:
        if pp.get('site_id') == site_id:
            return pp
    return None


def create_picking_point(picking_point_data: Dict) -> Dict:
    """Crea un nuevo picking point asociado a una sede"""
    picking_points = get_all_picking_points()
    
    new_pp = {
        'id': _get_next_id(picking_points),
        'site_id': picking_point_data['site_id'],
        'rappi_picking_point_id': picking_point_data.get('rappi_picking_point_id'),
        'external_id': picking_point_data.get('external_id'),
        'name': picking_point_data.get('name'),
        'address': picking_point_data.get('address'),
        'lat': picking_point_data.get('lat'),
        'lng': picking_point_data.get('lng'),
        'city': picking_point_data.get('city'),
        'phone': picking_point_data.get('phone'),
        'status': picking_point_data.get('status', 1),
        'created_at': _format_datetime(),
        'updated_at': None
    }
    
    picking_points.append(new_pp)
    _save_json(PICKING_POINTS_FILE, picking_points)
    return new_pp


def update_picking_point(picking_point_id: int, picking_point_data: Dict) -> Optional[Dict]:
    """Actualiza un picking point"""
    picking_points = get_all_picking_points()
    
    for i, pp in enumerate(picking_points):
        if pp.get('id') == picking_point_id:
            for key, value in picking_point_data.items():
                if value is not None:
                    pp[key] = value
            pp['updated_at'] = _format_datetime()
            picking_points[i] = pp
            _save_json(PICKING_POINTS_FILE, picking_points)
            return pp
    
    return None


def delete_picking_point(picking_point_id: int) -> bool:
    """Elimina un picking point"""
    picking_points = get_all_picking_points()
    original_count = len(picking_points)
    
    picking_points = [pp for pp in picking_points if pp.get('id') != picking_point_id]
    
    if len(picking_points) < original_count:
        _save_json(PICKING_POINTS_FILE, picking_points)
        return True
    return False


# ==================== APP CONFIG ====================

def get_app_config() -> Dict:
    """Obtiene la configuración de la aplicación"""
    default_config = {
        'validation_mode': 'polygons',  # 'polygons' o 'nearest_site'
        'colombia_delivery_mode': 'cargo',  # 'cargo' (Rappi Cargo) o 'calculated' (tarifa calculada)
        'max_delivery_distance_km': None,  # Distancia máxima en km (None = sin límite)
        'updated_at': _format_datetime()
    }
    config = _load_json(APP_CONFIG_FILE, default_config)
    # Asegurar que tiene los campos por defecto
    if 'validation_mode' not in config:
        config['validation_mode'] = default_config['validation_mode']
    if 'colombia_delivery_mode' not in config:
        config['colombia_delivery_mode'] = default_config['colombia_delivery_mode']
    if 'max_delivery_distance_km' not in config:
        config['max_delivery_distance_km'] = default_config['max_delivery_distance_km']
    return config


def update_app_config(config_data: Dict) -> Dict:
    """Actualiza la configuración de la aplicación"""
    current_config = get_app_config()
    current_config.update(config_data)
    current_config['updated_at'] = _format_datetime()
    _save_json(APP_CONFIG_FILE, current_config)
    return current_config


# ==================== SITE TARIFFS ====================

def get_all_site_tariffs() -> List[Dict]:
    """Obtiene todas las tarifas de sedes"""
    return _load_json(SITE_TARIFFS_FILE, [])


def get_site_tariff(site_id: int) -> Optional[Dict]:
    """Obtiene la tarifa de una sede por site_id"""
    tariffs = get_all_site_tariffs()
    for tariff in tariffs:
        if tariff.get('site_id') == site_id:
            return tariff
    return None


def create_site_tariff(tariff_data: Dict) -> Dict:
    """Crea una nueva tarifa de sede"""
    tariffs = get_all_site_tariffs()
    
    # Verificar si ya existe una tarifa para esta sede
    existing = get_site_tariff(tariff_data['site_id'])
    if existing:
        raise ValueError(f"Ya existe una tarifa para la sede {tariff_data['site_id']}")
    
    new_tariff = {
        'site_id': tariff_data['site_id'],
        'tariff_mode': tariff_data.get('tariff_mode', 'fixed'),
        'price_per_km': tariff_data['price_per_km'],
        'min_fee': tariff_data['min_fee'],
        'max_fee': tariff_data.get('max_fee'),
        'base_distance_km': tariff_data.get('base_distance_km'),
        'surcharge_per_km': tariff_data.get('surcharge_per_km'),
        'country': tariff_data.get('country'),
        'created_at': _format_datetime(),
        'updated_at': None
    }
    
    tariffs.append(new_tariff)
    _save_json(SITE_TARIFFS_FILE, tariffs)
    return new_tariff


def update_site_tariff(site_id: int, tariff_data: Dict) -> Optional[Dict]:
    """Actualiza la tarifa de una sede"""
    tariffs = get_all_site_tariffs()
    
    for i, tariff in enumerate(tariffs):
        if tariff.get('site_id') == site_id:
            # Si se está cambiando el modo de tarifa, limpiar campos no relevantes
            new_mode = tariff_data.get('tariff_mode')
            if new_mode:
                if new_mode == 'fixed':
                    # Limpiar campos de surcharge cuando se cambia a modo fijo
                    tariff['base_distance_km'] = None
                    tariff['surcharge_per_km'] = None
                elif new_mode == 'surcharge':
                    # Asegurar que los campos de surcharge estén presentes
                    if 'base_distance_km' not in tariff_data or tariff_data.get('base_distance_km') is None:
                        raise ValueError("Para el modo 'surcharge' se requiere 'base_distance_km'")
                    if 'surcharge_per_km' not in tariff_data or tariff_data.get('surcharge_per_km') is None:
                        raise ValueError("Para el modo 'surcharge' se requiere 'surcharge_per_km'")
            
            # Actualizar solo los campos proporcionados
            for key, value in tariff_data.items():
                if value is not None:
                    tariff[key] = value
                elif key in ['max_fee', 'base_distance_km', 'surcharge_per_km'] and key in tariff:
                    # Permitir eliminar estos campos estableciéndolos en None
                    tariff[key] = None
            
            tariff['updated_at'] = _format_datetime()
            tariffs[i] = tariff
            _save_json(SITE_TARIFFS_FILE, tariffs)
            return tariff
    
    return None


def delete_site_tariff(site_id: int) -> bool:
    """Elimina la tarifa de una sede"""
    tariffs = get_all_site_tariffs()
    
    for i, tariff in enumerate(tariffs):
        if tariff.get('site_id') == site_id:
            tariffs.pop(i)
            _save_json(SITE_TARIFFS_FILE, tariffs)
            return True
    
    return False


# ==================== ORDERS ====================

def get_all_orders() -> List[Dict]:
    """Obtiene todas las órdenes"""
    return _load_json(ORDERS_FILE, [])


def create_order(order_data: Dict) -> Dict:
    """Crea una nueva orden"""
    orders = get_all_orders()
    
    # Generar ID único
    new_id = 1
    if orders:
        new_id = max(order.get('id', 0) for order in orders) + 1
    
    order_data['id'] = new_id
    order_data['created_at'] = _format_datetime()
    
    # Si no tiene order_date, usar created_at
    if 'order_date' not in order_data or not order_data.get('order_date'):
        order_data['order_date'] = order_data['created_at']
    
    orders.append(order_data)
    _save_json(ORDERS_FILE, orders)
    return order_data


def get_orders_by_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None, cities: Optional[List[str]] = None) -> List[Dict]:
    """Obtiene órdenes filtradas por rango de fechas y/o ciudades"""
    orders = get_all_orders()
    
    # Verificar si hay algún filtro activo
    has_date_filter = start_date or end_date
    has_city_filter = cities and len(cities) > 0
    
    # Si no hay ningún filtro, devolver todas las órdenes
    if not has_date_filter and not has_city_filter:
        return orders
    
    filtered_orders = []
    for order in orders:
        # Filtrar por ciudades (múltiples) - este filtro es obligatorio si se proporciona
        if has_city_filter:
            order_city = order.get('city', '').strip().lower()
            # Verificar si la ciudad de la orden está en la lista de ciudades filtradas
            city_matches = any(
                city.strip().lower() == order_city 
                for city in cities
            )
            if not city_matches:
                continue  # Si no coincide con ninguna ciudad, excluir esta orden
        
        # Filtrar por fecha (solo si se proporcionan fechas)
        if has_date_filter:
            order_date_str = order.get('order_date', order.get('created_at', ''))
            
            if not order_date_str:
                # Si no tiene fecha y estamos filtrando por fecha, saltar
                continue
            else:
                # Normalizar fecha: tomar solo la parte de fecha (YYYY-MM-DD) si viene con hora
                order_date_normalized = order_date_str.split('T')[0] if 'T' in order_date_str else order_date_str.split(' ')[0]
                
                # Comparar fechas
                if start_date:
                    start_normalized = start_date.split('T')[0] if 'T' in start_date else start_date.split(' ')[0]
                    if order_date_normalized < start_normalized:
                        continue
                
                if end_date:
                    end_normalized = end_date.split('T')[0] if 'T' in end_date else end_date.split(' ')[0]
                    if order_date_normalized > end_normalized:
                        continue
        
        # Si llegamos aquí, la orden pasa todos los filtros
        filtered_orders.append(order)
    
    return filtered_orders
