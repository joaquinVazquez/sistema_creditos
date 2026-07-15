# app/routers/pago_router.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.pago_schema import PagoCreate, PagoResponse
from app.controllers.pago_controller import PagoController
from app.controllers.credito_controller import CreditoController

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])
pago_ctrl = PagoController()
credito_ctrl = CreditoController()

@router.post("/", status_code=201)
def registrar_abono(pago: PagoCreate):
    """Procesa un abono y actualiza el saldo del crédito atómicamente."""
    exito = pago_ctrl.registrar_pago(
        credito_id=pago.credito_id,
        usuario_id=pago.usuario_id,
        monto=pago.monto
    )
    if not exito:
        raise HTTPException(status_code=400, detail="Error transaccional al procesar el abono.")
    return {"mensaje": "Abono registrado correctamente"}

@router.get("/credito/{credito_id}", response_model=List[PagoResponse])
def historial_abonos(credito_id: int):
    """Retorna la sábana de pagos asociada a un crédito, incluyendo el cajero."""
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