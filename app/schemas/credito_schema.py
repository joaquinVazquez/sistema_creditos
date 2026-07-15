# app/schemas/credito_schema.py
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class CreditoCreate(BaseModel):
    rfc_cliente: str
    monto: float
    tasa_global: float
    plazos_semanas: int

class CreditoResponse(BaseModel):
    id: int
    fecha_inicio: date
    monto_original: Decimal
    tasa_interes_global: Decimal
    plazos_semanas: int
    saldo_actual: Decimal
    estado: str

    class Config:
        from_attributes = True