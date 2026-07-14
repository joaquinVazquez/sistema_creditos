from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    rfc = Column(String(13), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    telefono = Column(String(20))
    
    # Nuevos campos de expediente
    direccion = Column(String(255), nullable=True)
    foto_path = Column(String(500), nullable=True)
    ine_path = Column(String(500), nullable=True)
    
    # Auditoría
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())