"""
Servicio para validar direcciones con la API de Rappi
"""
import httpx
from typing import Optional, Dict, Any
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import settings
from app.core.rappi_config import get_order_validate_url, get_user_token


async def validate_order_with_rappi(
    address: str,
    lat: float,
    lng: float,
    city: str = "Bogota",
    total_value: float = 52000,
    user_tip: float = 3000,
    vehicle_type: str = "BIKE",
    payment_method: str = "ONLINE",
    external_picking_point_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Valida una dirección con la API de Rappi para verificar si es posible enviar un pedido.
    
    Args:
        address: Dirección del cliente
        lat: Latitud de la dirección
        lng: Longitud de la dirección
        city: Ciudad (por defecto: Bogota)
        total_value: Valor total del pedido (por defecto: 52000)
        user_tip: Propina del usuario (por defecto: 3000)
        vehicle_type: Tipo de vehículo (por defecto: BIKE)
        payment_method: Método de pago (por defecto: ONLINE)
    
    Returns:
        Dict con la respuesta de la API de Rappi si es exitosa, None si hay error
    """
    try:
        # Datos hardcodeados según lo solicitado
        payload = {
            "total_value": total_value,
            "user_tip": user_tip,
            "vehicle_type": vehicle_type,
            "payment_method": payment_method,
            "action_points": [
                {
                    "external_picking_point_id": external_picking_point_id,
                    "products": [],
                    "action_type": "PICK_UP",
                    "location_type": "STORE"
                },
                {
                    "products": [],
                    "action_type": "DROP_OFF",
                    "location_type": "CLIENT"
                }
            ],
            "client_info": {
                "email": "andrew19f@gmail.com",
                "phone": "573226892988",
                "first_name": "cliente",
                "last_name": "cliente",
                "address": address,
                "lat": lat,
                "lng": lng,
                "complement": "",
                "city": city,
                "comments": ""
            }
        }
        
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True  # Seguir redirecciones automáticamente
        ) as client:
            response = await client.post(
                get_order_validate_url(),
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
        print(f"Error al conectar con la API de Rappi: {e}")
        return None
    except httpx.HTTPStatusError as e:
        error_detail = ""
        error_data = None
        try:
            error_detail = e.response.text[:500]  # Limitar a 500 caracteres
            # Intentar parsear el JSON del error
            try:
                error_data = e.response.json()
            except:
                pass
        except:
            pass
        print(f"Error HTTP al validar con Rappi: {e.response.status_code}")
        if error_detail:
            print(f"Detalle: {error_detail}")
        if e.response.status_code == 307:
            print(f"Redirección detectada. URL de destino: {e.response.headers.get('Location', 'No disponible')}")
        
        # Si hay un error 400 con datos estructurados, retornarlos para mostrarlos al usuario
        if e.response.status_code == 400 and error_data:
            return {
                "error": {
                    "code": error_data.get("code"),
                    "i18n_code": error_data.get("i18n_code"),
                    "message": error_data.get("message"),
                    "internationalized_message": error_data.get("internationalized_message"),
                    "status": e.response.status_code
                }
            }
        
        return None
    except Exception as e:
        print(f"Error inesperado en validación Rappi: {e}")
        return None
