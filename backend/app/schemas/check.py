from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.schemas.polygon import PolygonResponse

class AddressCheck(BaseModel):
    """Dirección a verificar"""
    address: str = Field(..., min_length=1, description="Dirección a geocodificar y verificar")
    country: Optional[str] = Field("Colombia", description="País (por defecto: Colombia)")
    city: Optional[str] = Field(None, description="Ciudad")

class PolygonMatch(BaseModel):
    """Polígono que contiene la dirección"""
    polygon: PolygonResponse
    is_inside: bool
    site: Optional[Dict[str, Any]] = Field(None, description="Información de la sede asociada al polígono")

class RappiValidationError(BaseModel):
    """Error de validación de Rappi"""
    code: Optional[str] = Field(None, description="Código del error")
    i18n_code: Optional[str] = Field(None, description="Código de internacionalización")
    message: Optional[str] = Field(None, description="Mensaje de error")
    internationalized_message: Optional[str] = Field(None, description="Mensaje internacionalizado")
    status: Optional[int] = Field(None, description="Código de estado HTTP")

class RappiValidationResponse(BaseModel):
    """Respuesta de validación de Rappi"""
    service_delivery: Optional[List[str]] = Field(None, description="Tipos de servicio de entrega disponibles")
    active: Optional[bool] = Field(None, description="Indica si el servicio está activo")
    internal_validations: Optional[Dict[str, str]] = Field(None, description="Validaciones internas")
    eta_for_immediate_delivery: Optional[int] = Field(None, description="ETA para entrega inmediata en minutos")
    eta_interval_for_immediate_delivery: Optional[Dict[str, int]] = Field(None, description="Intervalo de ETA")
    trip_distance: Optional[float] = Field(None, description="Distancia del viaje en km")
    estimated_price: Optional[float] = Field(None, description="Precio estimado")
    rain_charge: Optional[bool] = Field(None, description="Cobro por lluvia")
    high_demand_charge: Optional[float] = Field(None, description="Cobro por alta demanda")
    raining_charge: Optional[float] = Field(None, description="Cobro por lluvia")
    error: Optional[RappiValidationError] = Field(None, description="Error de validación si existe")

class DeliveryPricingResponse(BaseModel):
    """Respuesta de cálculo de tarifas de entrega (para USA y España)"""
    price: Optional[float] = Field(None, description="Precio final de entrega")
    distance_km: Optional[float] = Field(None, description="Distancia en kilómetros")
    price_per_km: Optional[float] = Field(None, description="Precio por kilómetro")
    min_fee: Optional[float] = Field(None, description="Tarifa mínima")
    max_fee: Optional[float] = Field(None, description="Tarifa máxima (opcional)")
    country: Optional[str] = Field(None, description="País (usa, spain, colombia)")
    uses_rappi: bool = Field(False, description="Indica si usa Rappi Cargo")

class CheckAddressResponse(BaseModel):
    """Respuesta de verificación de dirección"""
    address: str
    formatted_address: Optional[str] = Field(None, description="Dirección formateada por Google Maps")
    latitude: Optional[float] = Field(None, description="Latitud obtenida de la geocodificación")
    longitude: Optional[float] = Field(None, description="Longitud obtenida de la geocodificación")
    geocoded: bool = Field(..., description="Indica si la dirección fue geocodificada exitosamente")
    is_inside_any: bool
    matching_polygons: List[PolygonMatch] = []
    rappi_validation: Optional[RappiValidationResponse] = Field(None, description="Validación de Rappi (solo Colombia)")
    delivery_pricing: Optional[DeliveryPricingResponse] = Field(None, description="Cálculo de tarifas (solo USA y España)")
    exceeds_max_distance: Optional[bool] = Field(None, description="Indica si la distancia excede el máximo configurado (solo si no está en polígono)")
    distance_to_site_km: Optional[float] = Field(None, description="Distancia en kilómetros desde la dirección hasta la sede")
