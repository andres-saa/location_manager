"""
Utilidades para cálculos geométricos
Implementación del algoritmo Ray Casting para determinar si un punto está dentro de un polígono
"""
import math
from typing import Tuple

def point_in_polygon(lat: float, lng: float, polygon_coordinates: list) -> bool:
    """
    Determina si un punto está dentro de un polígono usando el algoritmo Ray Casting.
    
    Args:
        lat: Latitud del punto
        lng: Longitud del punto
        polygon_coordinates: Lista de coordenadas del polígono [[lat, lng], ...]
    
    Returns:
        True si el punto está dentro del polígono, False en caso contrario
    """
    if len(polygon_coordinates) < 3:
        return False
    
    # Asegurar que el polígono esté cerrado (primer punto = último punto)
    coords = polygon_coordinates.copy()
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    
    inside = False
    j = len(coords) - 2  # Empezar desde el penúltimo punto
    
    for i in range(len(coords) - 1):
        lat_i, lng_i = coords[i]
        lat_j, lng_j = coords[j]
        
        # Algoritmo Ray Casting: verificar si el rayo horizontal cruza el borde
        # Intercambiamos lat/lng para trabajar con (x=lng, y=lat)
        if ((lng_i > lng) != (lng_j > lng)) and (lat < (lat_j - lat_i) * (lng - lng_i) / (lng_j - lng_i) + lat_i):
            inside = not inside
        
        j = i
    
    return inside

def validate_polygon_coordinates(coordinates: list) -> bool:
    """
    Valida que las coordenadas del polígono sean válidas.
    
    Args:
        coordinates: Lista de coordenadas [[lat, lng], ...]
    
    Returns:
        True si las coordenadas son válidas
    """
    if not coordinates or len(coordinates) < 3:
        return False
    
    for coord in coordinates:
        if not isinstance(coord, list) or len(coord) != 2:
            return False
        lat, lng = coord
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            return False
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return False
    
    return True

def calculate_polygon_center(polygon_coordinates: list) -> Tuple[float, float]:
    """
    Calcula el centro (centroide) de un polígono.
    
    Args:
        polygon_coordinates: Lista de coordenadas del polígono [[lat, lng], ...]
    
    Returns:
        Tupla (lat, lng) con el centro del polígono
    """
    if not polygon_coordinates or len(polygon_coordinates) < 3:
        return (0.0, 0.0)
    
    # Remover el último punto si es igual al primero (polígono cerrado)
    coords = polygon_coordinates.copy()
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    
    total_lat = 0.0
    total_lng = 0.0
    
    for coord in coords:
        lat, lng = coord
        total_lat += lat
        total_lng += lng
    
    count = len(coords)
    return (total_lat / count, total_lng / count)

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine.
    
    Args:
        lat1, lng1: Coordenadas del primer punto
        lat2, lng2: Coordenadas del segundo punto
    
    Returns:
        Distancia en kilómetros
    """
    # Radio de la Tierra en kilómetros
    R = 6371.0
    
    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Diferencia de coordenadas
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance
