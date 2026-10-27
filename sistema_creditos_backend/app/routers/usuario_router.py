# app/routers/usuario_router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.controllers.usuario_controller import UsuarioController
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])
controller = UsuarioController()

class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol_id: int

# Candado RBAC: Verificamos el token Y el nivel de privilegios
def verificar_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. Requiere privilegios de Administrador."
        )
    return current_user

@router.get("/")
def listar_usuarios(admin_user: Usuario = Depends(verificar_admin)):
    """Retorna la lista de empleados de la empresa."""
    try:
        return controller.obtener_usuarios_por_empresa(admin_user.empresa_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
def registrar_usuario(usuario: UsuarioCreate, admin_user: Usuario = Depends(verificar_admin)):
    """Da de alta a un nuevo empleado en la empresa."""
    resultado = controller.crear_usuario(
        empresa_id=admin_user.empresa_id,
        username=usuario.username,
        password=usuario.password,
        rol_id=usuario.rol_id
    )
    
    if resultado == "DUPLICADO":
        raise HTTPException(status_code=409, detail="El nombre de usuario ya está en uso.")
    if resultado == "ERROR":
        raise HTTPException(status_code=500, detail="Error en base de datos al guardar.")
        
    return {"mensaje": "Usuario creado exitosamente"}