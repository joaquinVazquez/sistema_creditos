# app/routers/cliente_router.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.cliente_schema import ClienteResponse, ClienteCreate
from app.controllers.cliente_controller import ClienteController

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])
controller = ClienteController()

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes():
    """Retorna la lista de clientes activos."""
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
def registrar_cliente(cliente: ClienteCreate):
    """Registra un nuevo cliente en el sistema."""
    exito = controller.guardar_cliente(
        rfc=cliente.rfc,
        nombre=cliente.nombre_completo,
        telefono=cliente.telefono,
        direccion=cliente.direccion
    )
    if not exito:
        raise HTTPException(status_code=400, detail="Error al registrar el cliente o RFC duplicado.")
    return {"mensaje": "Cliente registrado exitosamente", "rfc": cliente.rfc}