from datetime import date
from sqlalchemy import Column, Integer, Numeric, String, Date, ForeignKey
from app.models.database import Base

class Credito(Base):
    __tablename__ = "creditos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    monto_original = Column(Numeric(10, 2), nullable=False)
    tasa_interes_global = Column(Numeric(5, 2), nullable=False)
    plazos_semanas = Column(Integer, nullable=False)
    saldo_actual = Column(Numeric(10, 2), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    estado = Column(String(20), default="ACTIVO")
    
    # --- COLUMNAS LEGACY (Compatibilidad con v1.0) ---
    tasa_interes_mensual = Column(Numeric(5, 2), nullable=False, default=0.0)
    plazos_meses = Column(Integer, nullable=False, default=0)
    saldo_restante = Column(Numeric(10, 2), nullable=False, default=0.0)
    fecha_otorgamiento = Column(Date, nullable=False, default=date.today)