# app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.database import SessionLocal
from app.models.usuario import Usuario

# Le indicamos a FastAPI en qué ruta se obtienen los tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    """Generador de sesiones de base de datos para las dependencias."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """Desencripta el JWT y extrae al usuario que está haciendo la petición."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Intentamos abrir el token con nuestra llave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Validamos que el usuario siga existiendo y esté activo en la base de datos
    user = db.query(Usuario).filter(Usuario.username == username, Usuario.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user