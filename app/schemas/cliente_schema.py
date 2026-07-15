# app/schemas/cliente_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    rfc: str
    nombre_completo: str
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    direccion: Optional[str] = None

class ClienteResponse(ClienteBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True