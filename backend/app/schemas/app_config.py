"""
Schemas para la configuración de la aplicación
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional

class AppConfigUpdate(BaseModel):
    """Datos para actualizar la configuración de la aplicación"""
    validation_mode: Literal['polygons', 'nearest_site'] = Field(
        ...,
        description="Modo de validación: 'polygons' (usar polígonos) o 'nearest_site' (sede más cercana)"
    )
    colombia_delivery_mode: Optional[Literal['cargo', 'calculated']] = Field(
        None,
        description="Modo de entrega para Colombia: 'cargo' (Rappi Cargo) o 'calculated' (tarifa calculada). Solo aplica para Colombia."
    )
    max_delivery_distance_km: Optional[float] = Field(
        None,
        ge=0,
        description="Distancia máxima en kilómetros para entregas. Si la dirección está dentro de un polígono, esta distancia se ignora."
    )

class AppConfigResponse(BaseModel):
    """Respuesta de configuración de la aplicación"""
    validation_mode: str = Field(..., description="Modo de validación actual")
    colombia_delivery_mode: Optional[str] = Field(None, description="Modo de entrega para Colombia: 'cargo' o 'calculated'")
    max_delivery_distance_km: Optional[float] = Field(None, description="Distancia máxima en kilómetros para entregas")
    updated_at: str = Field(..., description="Fecha de última actualización")
