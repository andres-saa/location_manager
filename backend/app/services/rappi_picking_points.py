"""
Servicio para gestionar picking points de Rappi Cargo
"""
import httpx
import json
from typing import Optional, Dict, Any, List
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import settings
from app.core.rappi_config import (
    get_picking_point_url,
    get_picking_point_list_url,
    get_user_token
)


async def create_picking_point(
    lat: float,
    lng: float,
    address: str,
    city: str,
    phone: str,
    zip_code: Optional[str] = None,
    status: int = 1,
    name: str = "",
    contact_name: str = "",
    contact_email: str = "",
    preparation_time: int = 30,
    external_id: str = "",
    rappi_store_id: Optional[int] = None,
    default_tip: int = 500,
    handshake_enabled: bool = True,
    return_enabled: bool = True,
    handoff_enabled: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Crea un picking point en Rappi Cargo.
    
    Returns:
        Dict con la respuesta de la API de Rappi si es exitosa, None si hay error
    """
    try:
        payload = {
            "lat": lat,
            "lng": lng,
            "address": address,
            "city": city,
            "phone": phone,
            "zip_code": zip_code or "",
            "status": status,
            "name": name,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "preparation_time": preparation_time,
            "external_id": external_id,
            "default_tip": default_tip,
            "handshake_enabled": handshake_enabled,
            "return_enabled": return_enabled,
            "handoff_enabled": handoff_enabled
        }
        
        # Agregar rappi_store_id solo si se proporciona
        if rappi_store_id is not None:
            payload["rappi_store_id"] = rappi_store_id
        
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True
        ) as client:
            response = await client.post(
                get_picking_point_url(),
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "user-token": get_user_token()
                }
            )
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.RequestError as e:
        print(f"Error al conectar con la API de Rappi para crear picking point: {e}")
        return None
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text[:500]
        except:
            pass
        print(f"Error HTTP al crear picking point: {e.response.status_code}")
        if error_detail:
            print(f"Detalle: {error_detail}")
        return None
    except Exception as e:
        print(f"Error inesperado al crear picking point: {e}")
        return None


async def update_picking_point(
    picking_point_id: int,
    lat: float,
    lng: float,
    address: str,
    city: str,
    phone: str,
    zip_code: Optional[str] = None,
    status: int = 1,
    name: str = "",
    contact_name: str = "",
    contact_email: str = "",
    preparation_time: int = 30,
    external_id: str = "",
    rappi_store_id: Optional[int] = None,
    default_tip: int = 500,
    handshake_enabled: bool = True,
    return_enabled: bool = True,
    handoff_enabled: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Actualiza un picking point en Rappi Cargo.
    
    Args:
        picking_point_id: ID del picking point en Rappi a actualizar
    
    Returns:
        Dict con la respuesta de la API de Rappi si es exitosa, None si hay error
    """
    try:
        payload = {
            "id": picking_point_id,
            "lat": lat,
            "lng": lng,
            "address": address,
            "city": city,
            "phone": phone,
            "zip_code": zip_code or "",
            "status": status,
            "name": name,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "preparation_time": preparation_time,
            "external_id": external_id,
            "default_tip": default_tip,
            "handshake_enabled": handshake_enabled,
            "return_enabled": return_enabled,
            "handoff_enabled": handoff_enabled
        }
        
        # Agregar rappi_store_id solo si se proporciona
        if rappi_store_id is not None:
            payload["rappi_store_id"] = rappi_store_id
        
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True
        ) as client:
            response = await client.put(
                get_picking_point_url(),  # Mismo endpoint, pero con PUT
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "user-token": get_user_token()
                }
            )
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.RequestError as e:
        print(f"Error al conectar con la API de Rappi para actualizar picking point: {e}")
        return None
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text[:500]
        except:
            pass
        print(f"Error HTTP al actualizar picking point: {e.response.status_code}")
        if error_detail:
            print(f"Detalle: {error_detail}")
        return None
    except Exception as e:
        print(f"Error inesperado al actualizar picking point: {e}")
        return None


async def delete_picking_point(picking_point_id: int) -> bool:
    """
    Elimina un picking point en Rappi Cargo.
    
    Args:
        picking_point_id: ID del picking point en Rappi a eliminar
    
    Returns:
        True si se eliminó exitosamente, False si hay error
    """
    try:
        payload = {
            "id": picking_point_id
        }
        print(f"Eliminando picking point de Rappi con ID: {picking_point_id}")
        print(f"Payload: {payload}")
        
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True
        ) as client:
            response = await client.request(
                "DELETE",
                get_picking_point_url(),
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "user-token": get_user_token()
                }
            )
            # 204 es el código de éxito para DELETE
            if response.status_code == 204:
                return True
            response.raise_for_status()
            return True
    except httpx.RequestError as e:
        print(f"Error al conectar con la API de Rappi para eliminar picking point: {e}")
        return False
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text[:500]
        except:
            pass
        print(f"Error HTTP al eliminar picking point: {e.response.status_code}")
        if error_detail:
            print(f"Detalle: {error_detail}")
        return False
    except Exception as e:
        print(f"Error inesperado al eliminar picking point: {e}")
        return False


async def list_picking_points() -> List[Dict[str, Any]]:
    """
    Lista todos los picking points de Rappi Cargo.
    
    Returns:
        Lista de picking points
    """
    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True
        ) as client:
            response = await client.get(
                get_picking_point_list_url(),
                headers={
                    "Content-Type": "application/json",
                    "user-token": get_user_token()
                }
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
    except httpx.RequestError as e:
        print(f"Error al conectar con la API de Rappi para listar picking points: {e}")
        return []
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.text[:500]
        except:
            pass
        print(f"Error HTTP al listar picking points: {e.response.status_code}")
        if error_detail:
            print(f"Detalle: {error_detail}")
        return []
    except Exception as e:
        print(f"Error inesperado al listar picking points: {e}")
        return []
