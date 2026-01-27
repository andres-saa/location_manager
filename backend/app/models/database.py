from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

# Agregar el directorio raíz al path si es necesario
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import Base

class Polygon(Base):
    """Modelo para almacenar polígonos de Google Maps"""
    __tablename__ = "polygons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    coordinates = Column(JSON, nullable=False)  # Lista de [lat, lng]
    color = Column(String, default="#FF0000")  # Color para visualización
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con locaciones
    locations = relationship("Location", back_populates="polygon", cascade="all, delete-orphan")

class Location(Base):
    """Modelo para almacenar locaciones"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    polygon_id = Column(Integer, ForeignKey("polygons.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con polígono
    polygon = relationship("Polygon", back_populates="locations")
