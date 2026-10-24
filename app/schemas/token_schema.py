# app/schemas/token_schema.py
from pydantic import BaseModel

class UsuarioToken(BaseModel):
    id: int
    username: str
    rol_id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioToken