from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nombre de la locación")
    description: Optional[str] = Field(None, description="Descripción de la locación")
    latitude: float = Field(..., ge=-90, le=90, description="Latitud")
    longitude: float = Field(..., ge=-180, le=180, description="Longitud")
    address: Optional[str] = Field(None, description="Dirección")
    polygon_id: Optional[int] = Field(None, description="ID del polígono asociado")

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    polygon_id: Optional[int] = None

class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
