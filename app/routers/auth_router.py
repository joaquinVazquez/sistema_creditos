# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.database import SessionLocal
from app.models.usuario import Usuario
from app.core.security import verificar_password, crear_token_acceso
from app.schemas.token_schema import Token

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Valida credenciales y emite un JWT para acceso a la API."""
    db = SessionLocal()
    try:
        # 1. Buscar al usuario activo en la base de datos
        usuario = db.query(Usuario).filter(Usuario.username == form_data.username, Usuario.is_active == True).first()
        
        # 2. Validación de credenciales
        # NOTA DE MIGRACIÓN: Si en la v1.0 las contraseñas están en texto plano, 
        # reemplaza temporalmente 'verificar_password' por 'form_data.password == usuario.password_hash'
        if not usuario or not verificar_password(form_data.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 3. Empaquetar payload y firmar JWT
        token_payload = {
            "sub": str(usuario.id), 
            "username": usuario.username
        }
        access_token = crear_token_acceso(data=token_payload)
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"[ERROR AUTH]: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        db.close()