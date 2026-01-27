"""
Esquemas para configurar tarifas de entrega por sede (USA y España)
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

class SiteTariffCreate(BaseModel):
    site_id: int = Field(..., description="ID de la sede")
    tariff_mode: Literal['fixed', 'surcharge'] = Field(
        'fixed',
        description="Modo de tarifa: 'fixed' (tarifa fija por km) o 'surcharge' (con recargo después de distancia base)"
    )
    price_per_km: float = Field(..., gt=0, description="Precio por kilómetro (para modo 'fixed' o precio base para 'surcharge')")
    min_fee: float = Field(..., gt=0, description="Tarifa mínima de entrega")
    max_fee: Optional[float] = Field(None, gt=0, description="Tarifa máxima de entrega (opcional)")
    # Campos para modo 'surcharge'
    base_distance_km: Optional[float] = Field(None, gt=0, description="Distancia base en km antes de aplicar recargo (solo para modo 'surcharge')")
    surcharge_per_km: Optional[float] = Field(None, gt=0, description="Precio adicional por km después de la distancia base (solo para modo 'surcharge')")

class SiteTariffUpdate(BaseModel):
    tariff_mode: Optional[Literal['fixed', 'surcharge']] = Field(
        None,
        description="Modo de tarifa: 'fixed' (tarifa fija por km) o 'surcharge' (con recargo después de distancia base)"
    )
    price_per_km: Optional[float] = Field(None, gt=0, description="Precio por kilómetro")
    min_fee: Optional[float] = Field(None, gt=0, description="Tarifa mínima de entrega")
    max_fee: Optional[float] = Field(None, gt=0, description="Tarifa máxima de entrega (opcional, None para eliminar)")
    # Campos para modo 'surcharge'
    base_distance_km: Optional[float] = Field(None, gt=0, description="Distancia base en km antes de aplicar recargo (solo para modo 'surcharge')")
    surcharge_per_km: Optional[float] = Field(None, gt=0, description="Precio adicional por km después de la distancia base (solo para modo 'surcharge')")

class SiteTariffResponse(BaseModel):
    site_id: int = Field(..., description="ID de la sede")
    tariff_mode: str = Field('fixed', description="Modo de tarifa: 'fixed' o 'surcharge'")
    price_per_km: float = Field(..., description="Precio por kilómetro")
    min_fee: float = Field(..., description="Tarifa mínima de entrega")
    max_fee: Optional[float] = Field(None, description="Tarifa máxima de entrega")
    base_distance_km: Optional[float] = Field(None, description="Distancia base en km (solo para modo 'surcharge')")
    surcharge_per_km: Optional[float] = Field(None, description="Precio adicional por km después de la distancia base (solo para modo 'surcharge')")
    country: str = Field(..., description="País de la sede")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: Optional[str] = Field(None, description="Fecha de última actualización")
