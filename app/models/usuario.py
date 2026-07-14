from sqlalchemy import Column, Integer, String, Boolean
from app.models.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer) # Mapeo básico para satisfacer la llave foránea
    is_active = Column(Boolean, default=True)