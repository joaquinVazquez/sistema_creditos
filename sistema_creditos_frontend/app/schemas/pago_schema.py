# app/schemas/pago_schema.py
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class PagoCreate(BaseModel):
    credito_id: int
    usuario_id: int
    monto: float

class PagoResponse(BaseModel):
    id: int
    fecha: datetime
    monto: Decimal
    username: str

    class Config:
        from_attributes = True