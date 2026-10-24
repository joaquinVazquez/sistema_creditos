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

class ClienteCreate(BaseModel):
    rfc: str
    nombre_completo: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    foto_path: Optional[str] = None
    ine_path: Optional[str] = None

# --- ESQUEMA TEMPORAL PARA EDICIÓN ---
class ClienteUpdate(BaseModel):
    rfc: Optional[str] = None
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    foto_path: Optional[str] = None 
    ine_path: Optional[str] = None

# --- RUTAS EXISTENTES ---

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(skip: int = 0, limit: int = 50, incluir_inactivos: bool = False, current_user: Usuario = Depends(get_current_user)):
    """Retorna el directorio de clientes, con opción a incluir archivados."""
    try:
        # Pasamos el nuevo parámetro al controlador
        clientes_tuplas = controller.obtener_todos(skip=skip, limit=limit, incluir_inactivos=incluir_inactivos)
        resultado = []
        for c in clientes_tuplas:
            resultado.append({
                "rfc": c[0],
                "nombre_completo": c[1],
                "telefono": c[2],
                "created_at": c[3],
                "activo": c[4] # <-- Agregamos el estado para el frontend
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR EN AUDITORÍA DE CLIENTES: {str(e)}")

@router.post("/", status_code=201)
def registrar_cliente(cliente: ClienteCreate, current_user: Usuario = Depends(get_current_user)):
    """Registra un nuevo cliente (Ruta Protegida)."""
    try:
        resultado = controller.guardar_cliente(
            rfc=cliente.rfc,
            nombre=cliente.nombre_completo,
            telefono=cliente.telefono,
            direccion=cliente.direccion,
            foto_path=cliente.foto_path,
            ine_path=cliente.ine_path
        )
        
        if resultado == "DUPLICADO":
            # Disparamos error 409 para que el frontend sepa que está repetido
            raise HTTPException(status_code=409, detail="El RFC ya se encuentra registrado.")
        elif resultado != "EXITO":
            raise HTTPException(status_code=400, detail="Error en base de datos al guardar.")
            
        return {"mensaje": "Cliente registrado exitosamente", "rfc": cliente.rfc}
    except HTTPException:
        raise # Permite que los errores 409 y 400 pasen limpios
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

@router.patch("/{rfc}/archivar", status_code=200)
def archivar_cliente(rfc: str, current_user: Usuario = Depends(get_current_user)):
    """Oculta un cliente del directorio principal (Soft Delete)."""
    try:
        exito = controller.archivar_cliente(rfc)
        if not exito:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
        return {"mensaje": "Cliente archivado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR AL ARCHIVAR CLIENTE: {str(e)}")

@router.patch("/{rfc}/desarchivar", status_code=200)
def desarchivar_cliente(rfc: str, current_user: Usuario = Depends(get_current_user)):
    """Restaura un cliente del archivo (Soft Delete Inverso)."""
    try:
        exito = controller.desarchivar_cliente(rfc)
        if not exito:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
        return {"mensaje": "Cliente reactivado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR AL REACTIVAR CLIENTE: {str(e)}")