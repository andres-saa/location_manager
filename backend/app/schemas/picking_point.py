from pydantic import BaseModel, Field
from typing import Optional

class PickingPointCreate(BaseModel):
    """Datos para crear un picking point"""
    site_id: int = Field(..., description="ID de la sede asociada")
    lat: float = Field(..., description="Latitud")
    lng: float = Field(..., description="Longitud")
    address: str = Field(..., description="Dirección")
    city: str = Field(..., description="Ciudad")
    phone: str = Field(..., description="Teléfono")
    zip_code: Optional[str] = Field(None, description="Código postal")
    status: int = Field(1, description="Estado (1=activo)")
    name: str = Field(..., description="Nombre del picking point")
    contact_name: str = Field(..., description="Nombre del contacto")
    contact_email: str = Field(..., description="Email del contacto")
    preparation_time: int = Field(30, description="Tiempo de preparación en minutos")
    external_id: str = Field(..., description="ID externo")
    rappi_store_id: Optional[int] = Field(None, description="ID de la tienda Rappi")
    default_tip: int = Field(500, description="Propina por defecto")
    handshake_enabled: bool = Field(True, description="Handshake habilitado")
    return_enabled: bool = Field(True, description="Retorno habilitado")
    handoff_enabled: bool = Field(True, description="Handoff habilitado")

class PickingPointResponse(BaseModel):
    """Respuesta de picking point"""
    id: int
    site_id: int
    rappi_picking_point_id: Optional[int] = None
    external_id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[int] = None
    created_at: str
    updated_at: Optional[str] = None
