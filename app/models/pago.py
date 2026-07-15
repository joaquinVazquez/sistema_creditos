from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    credito_id = Column(Integer, ForeignKey("creditos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha = Column(DateTime, server_default=func.now())

    # --- COLUMNAS LEGACY (Soportadas para evitar NotNullViolation) ---
    monto_pagado = Column(Numeric(10, 2), nullable=True)
    fecha_pago = Column(DateTime, server_default=func.now())