# app/routers/cliente_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.cliente_schema import ClienteResponse, ClienteCreate
from app.controllers.cliente_controller import ClienteController

# Importaciones de seguridad CRÍTICAS
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])
controller = ClienteController()

# --- ESQUEMA TEMPORAL PARA EDICIÓN ---
class ClienteUpdate(BaseModel):
    rfc: Optional[str] = None
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

# --- RUTAS EXISTENTES ---

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
        raise HTTPException(status_code=500, detail=f"ERROR EN CLIENTES DETALLADO: {str(e)}")

@router.post("/", status_code=201)
def registrar_cliente(cliente: ClienteCreate, current_user: Usuario = Depends(get_current_user)):
    """Registra un nuevo cliente (Ruta Protegida)."""
    try:
        exito = controller.guardar_cliente(
            rfc=cliente.rfc,
            nombre=cliente.nombre_completo,
            telefono=cliente.telefono,
            direccion=cliente.direccion
        )
        if not exito:
            raise HTTPException(status_code=400, detail="Error en base de datos al guardar.")
        return {"mensaje": "Cliente registrado exitosamente", "rfc": cliente.rfc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR AL REGISTRAR CLIENTE: {str(e)}")

# --- NUEVAS RUTAS PARA EDICIÓN ---

@router.get("/{rfc}")
def obtener_cliente(rfc: str, current_user: Usuario = Depends(get_current_user)):
    """Obtiene los datos de un cliente específico para llenar el formulario de edición."""
    try:
        datos = controller.obtener_cliente_por_rfc(rfc)
        if not datos:
            raise HTTPException(status_code=404, detail="Cliente no encontrado en la base de datos.")
        # Devuelve la tupla directamente para que el frontend la lea: [rfc, nombre, telefono, ...]
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR AL OBTENER CLIENTE: {str(e)}")

@router.put("/{rfc_original}")
def actualizar_cliente(rfc_original: str, cliente_data: ClienteUpdate, current_user: Usuario = Depends(get_current_user)):
    """Actualiza los datos de un cliente existente."""
    try:
        # Convierte el modelo a un diccionario ignorando los valores que el frontend no envió
        datos_nuevos = cliente_data.dict(exclude_unset=True) 
        exito = controller.actualizar_cliente(rfc_original, datos_nuevos)
        
        if not exito:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el cliente.")
        return {"mensaje": "Cliente actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR AL ACTUALIZAR: {str(e)}")