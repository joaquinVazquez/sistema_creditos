# app/routers/pago_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.pago_schema import PagoCreate, PagoResponse
from app.controllers.pago_controller import PagoController
from app.controllers.credito_controller import CreditoController

# Importaciones de seguridad
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])
pago_ctrl = PagoController()
credito_ctrl = CreditoController()

@router.post("/", status_code=201)
def registrar_abono(pago: PagoCreate, current_user: Usuario = Depends(get_current_user)):
    """Procesa un abono y actualiza el saldo del crédito atómicamente (Ruta Protegida)."""
    exito = pago_ctrl.registrar_pago(
        credito_id=pago.credito_id,
        usuario_id=pago.usuario_id,
        monto=pago.monto
    )
    if not exito:
        raise HTTPException(status_code=400, detail="Error transaccional al procesar el abono.")
    return {"mensaje": "Abono registrado correctamente"}

@router.get("/credito/{credito_id}", response_model=List[PagoResponse])
def historial_abonos(credito_id: int, current_user: Usuario = Depends(get_current_user)):
    """Retorna la sábana de pagos asociada a un crédito, incluyendo el cajero (Ruta Protegida)."""
    try:
        pagos_tuplas = credito_ctrl.obtener_pagos_por_credito(credito_id)
        resultado = []
        for p in pagos_tuplas:
            resultado.append({
                "id": p[0],
                "fecha": p[1],
                "monto": p[2],
                "username": p[3]
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))