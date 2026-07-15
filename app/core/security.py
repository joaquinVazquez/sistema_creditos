# app/core/security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import os

# 1. Configuración del motor de encriptación (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Variables de Entorno para el Token
# (En producción, SECRET_KEY debe ir en tu archivo .env)
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # El token durará 24 horas en desarrollo

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano contra el hash de la base de datos."""
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password: str) -> str:
    """Genera el hash irreversible para guardar contraseñas nuevas."""
    return pwd_context.hash(password)

def crear_token_acceso(data: dict) -> str:
    """Genera el JWT (Gafete Virtual) con los datos del usuario y tiempo de expiración."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Firmamos el token con nuestra llave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt