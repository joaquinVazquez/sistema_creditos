# app/routers/credito_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.credito_schema import CreditoCreate, CreditoResponse
from app.controllers.credito_controller import CreditoController

# Importaciones de seguridad
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/creditos", tags=["Créditos"])
controller = CreditoController()

@router.post("/", status_code=201)
def crear_credito(credito: CreditoCreate, current_user: Usuario = Depends(get_current_user)):
    """Procesa un nuevo crédito atado al RFC del cliente (Ruta Protegida)."""
    exito = controller.crear_credito(
        rfc_cliente=credito.rfc_cliente,
        monto=credito.monto,
        tasa_global=credito.tasa_global,
        plazos_semanas=credito.plazos_semanas
    )
    if not exito:
        raise HTTPException(status_code=400, detail="Error transaccional. Verifica el RFC o la base de datos.")
    return {"mensaje": "Crédito generado exitosamente"}

@router.get("/{rfc}", response_model=List[CreditoResponse])
def historial_creditos(rfc: str, current_user: Usuario = Depends(get_current_user)):
    """Retorna el historial completo de créditos de un cliente específico (Ruta Protegida)."""
    try:
        creditos_tuplas = controller.obtener_historial_por_rfc(rfc)
        resultado = []
        for c in creditos_tuplas:
            resultado.append({
                "id": c[0],
                "fecha_inicio": c[1],
                "monto_original": c[2],
                "tasa_interes_global": c[3],
                "plazos_semanas": c[4],
                "saldo_actual": c[5],
                "estado": c[6]
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))