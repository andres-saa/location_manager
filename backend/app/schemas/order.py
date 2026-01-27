"""
Schemas para órdenes/pedidos
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class OrderCreate(BaseModel):
    """Datos para crear una orden/pedido"""
    latitude: float = Field(..., description="Latitud de la dirección de entrega")
    longitude: float = Field(..., description="Longitud de la dirección de entrega")
    address: str = Field(..., description="Dirección completa de entrega")
    formatted_address: Optional[str] = Field(None, description="Dirección formateada de Rappi Cargo (sin información de zonas)")
    first_name: str = Field(..., description="Nombre del cliente")
    last_name: str = Field(..., description="Apellido del cliente")
    phone: str = Field(..., description="Teléfono del cliente")
    email: EmailStr = Field(..., description="Correo electrónico del cliente")
    complement: Optional[str] = Field(None, description="Complemento de la dirección (apto, torre, etc.)")
    city: Optional[str] = Field(None, description="Ciudad")
    country: Optional[str] = Field(None, description="País: 'colombia', 'usa', 'spain'")
    comments: Optional[str] = Field(None, description="Comentarios adicionales")
    order_date: Optional[datetime] = Field(None, description="Fecha de la orden (si no se proporciona, se usa la fecha actual)")

class OrderResponse(BaseModel):
    """Respuesta de una orden/pedido"""
    id: int = Field(..., description="ID único de la orden")
    latitude: float = Field(..., description="Latitud de la dirección de entrega")
    longitude: float = Field(..., description="Longitud de la dirección de entrega")
    address: str = Field(..., description="Dirección completa de entrega")
    formatted_address: Optional[str] = Field(None, description="Dirección formateada de Rappi Cargo")
    first_name: str = Field(..., description="Nombre del cliente")
    last_name: str = Field(..., description="Apellido del cliente")
    phone: str = Field(..., description="Teléfono del cliente")
    email: str = Field(..., description="Correo electrónico del cliente")
    complement: Optional[str] = Field(None, description="Complemento de la dirección")
    city: Optional[str] = Field(None, description="Ciudad")
    country: Optional[str] = Field(None, description="País: 'colombia', 'usa', 'spain'")
    comments: Optional[str] = Field(None, description="Comentarios adicionales")
    order_date: str = Field(..., description="Fecha de la orden (ISO format)")
    created_at: str = Field(..., description="Fecha de creación del registro (ISO format)")

class OrderListResponse(BaseModel):
    """Respuesta de lista de órdenes con estadísticas"""
    orders: list[OrderResponse] = Field(..., description="Lista de órdenes")
    total: int = Field(..., description="Total de órdenes")
    zone_stats: dict = Field(..., description="Estadísticas por zona/polígono")
