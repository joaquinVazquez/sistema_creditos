# app/routers/cliente_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.cliente_schema import ClienteResponse, ClienteCreate
from app.controllers.cliente_controller import ClienteController

# Importaciones de seguridad CRÍTICAS para que FastAPI reconozca las dependencias
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])
controller = ClienteController()

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(current_user: Usuario = Depends(get_current_user)):
    """Retorna la lista de clientes (Ruta Protegida)."""
    try:
        clientes_tuplas = controller.obtener_todos()
        resultado = []
        for c in clientes_tuplas:
            resultado.append({
                "rfc": c[0],
                "nombre_completo": c[1],
                "telefono": c[2],
                "created_at": c[3]
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
def registrar_cliente(cliente: ClienteCreate, current_user: Usuario = Depends(get_current_user)):
    """Registra un nuevo cliente (Ruta Protegida)."""
    exito = controller.guardar_cliente(
        rfc=cliente.rfc,
        nombre=cliente.nombre_completo,
        telefono=cliente.telefono,
        direccion=cliente.direccion
    )
    if not exito:
        raise HTTPException(status_code=400, detail="Error al registrar o RFC duplicado.")
    return {"mensaje": "Cliente registrado exitosamente", "rfc": cliente.rfc}