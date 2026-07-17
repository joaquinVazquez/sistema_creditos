# app/core/security.py
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import os

# 1. Variables de Entorno para el Token
# CRÍTICO: SECRET_KEY debe venir SIEMPRE de una variable de entorno.
# Nunca hardcodear un valor por defecto aquí: si esta clave se filtra
# (por ejemplo en un repositorio público), cualquiera puede firmar
# tokens JWT falsos y saltarse el login.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "CRÍTICO: No se encontró la variable de entorno SECRET_KEY.\n"
        "Defínela en tu archivo .env (local) o en las variables de entorno "
        "de Render (producción) antes de iniciar la aplicación."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # El token durará 24 horas

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano contra el hash usando bcrypt nativo."""
    # Convertimos la contraseña plana a bytes
    password_bytes = plain_password.encode('utf-8')

    # Estandarizamos el hash proveniente de PostgreSQL a bytes
    if isinstance(hashed_password, str):
        hash_bytes = hashed_password.encode('utf-8')
    elif isinstance(hashed_password, memoryview):
        hash_bytes = hashed_password.tobytes()
    else:
        hash_bytes = hashed_password

    try:
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"[ERROR BCRYPT NATIVO]: {e}")
        return False

def obtener_password_hash(password: str) -> str:
    """Genera el hash irreversible para guardar contraseñas nuevas."""
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

def crear_token_acceso(data: dict) -> str:
    """Genera el JWT (Gafete Virtual) con los datos del usuario."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Firmamos el token con nuestra llave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt