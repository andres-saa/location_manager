from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Coordinate(BaseModel):
    """Coordenada individual [lat, lng]"""
    lat: float = Field(..., description="Latitud")
    lng: float = Field(..., description="Longitud")

class PolygonBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nombre del polígono")
    description: Optional[str] = Field(None, description="Descripción del polígono")
    coordinates: List[List[float]] = Field(..., min_items=3, description="Lista de coordenadas [lat, lng]")
    color: Optional[str] = Field("#FF0000", description="Color en formato hexadecimal")
    site_id: Optional[int] = Field(None, description="ID de la sede asociada")
    country: Optional[str] = Field(None, description="País del polígono: 'colombia', 'usa', 'spain'")

class PolygonCreate(PolygonBase):
    pass

class PolygonUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    coordinates: Optional[List[List[float]]] = None
    color: Optional[str] = None
    site_id: Optional[int] = None
    country: Optional[str] = None

class PolygonResponse(PolygonBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
