# app/models/clientes.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    rfc = Column(String(13), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(255), nullable=True)
    foto_path = Column(String(255), nullable=True)
    ine_path = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # COLUMNA MULTI-TENANT (Faltaba esta declaración)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, default=1)