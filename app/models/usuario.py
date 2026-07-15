# app/models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean
from app.models.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Columnas que le faltaban al ORM pero que el SQL crudo sí usaba
    rol_id = Column(Integer, nullable=False, default=1)
    activo = Column(Boolean, default=True)