# app/models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.models.database import Base
from app.models.empresa import Empresa

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Columnas operativas
    rol_id = Column(Integer, nullable=False, default=1)
    activo = Column(Boolean, default=True)
    
    # El candado Multi-tenant (SaaS)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, default=1)