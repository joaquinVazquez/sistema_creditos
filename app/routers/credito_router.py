from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.schemas.credito_schema import CreditoCreate, CreditoResponse
from app.controllers.credito_controller import CreditoController
from app.core.dependencies import get_current_user, get_db
from app.models.usuario import Usuario
from app.models.credito import Credito
from app.models.clientes import Cliente
from app.models.pago import Pago

router = APIRouter(prefix="/api/v1/creditos", tags=["Créditos"])
controller = CreditoController()

@router.post("/", status_code=201)
def crear_credito(credito: CreditoCreate, current_user: Usuario = Depends(get_current_user)):
    exito = controller.crear_credito(credito.rfc_cliente, credito.monto, credito.tasa_global, credito.plazos_semanas)
    if not exito: raise HTTPException(status_code=400, detail="Error transaccional en base de datos.")
    return {"mensaje": "Crédito generado exitosamente"}

@router.get("/historial/{rfc}", response_model=List[CreditoResponse])
def historial_creditos(rfc: str, current_user: Usuario = Depends(get_current_user)):
    try:
        tuplas = controller.obtener_historial_por_rfc(rfc)
        return [{"id": c[0], "fecha_inicio": c[1], "monto_original": c[2], "tasa_interes_global": c[3], "plazos_semanas": c[4], "saldo_actual": c[5], "estado": c[6]} for c in tuplas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id_credito}/pagos")
def historial_abonos(id_credito: int, current_user: Usuario = Depends(get_current_user)):
    try:
        tuplas = controller.obtener_pagos_por_credito(id_credito)
        # Se formatea a float para garantizar la serialización JSON
        return [{"id": p[0], "fecha": p[1], "monto": float(p[2]), "username": p[3]} for p in tuplas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cliente/{rfc}/activos")
def get_creditos_activos(rfc: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    creditos = db.query(Credito).join(Cliente).filter(Cliente.rfc == rfc, Credito.estado == "ACTIVO").all()
    return [{"id": c.id, "monto_original": c.monto_original, "saldo_actual": c.saldo_actual, "estado": c.estado, "fecha_inicio": c.fecha_inicio} for c in creditos]

@router.get("/{id_credito}/metricas")
def get_metricas(id_credito: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    credito = db.query(Credito).filter(Credito.id == id_credito).first()
    if not credito: raise HTTPException(status_code=404, detail="Crédito no encontrado")
    
    pagos_count = db.query(func.count(Pago.id)).filter(Pago.credito_id == id_credito).scalar()
    deuda = credito.monto_original * (1 + (credito.tasa_interes_global / 100))
    cuota = deuda / credito.plazos_semanas if credito.plazos_semanas > 0 else 0
    
    return {"cuota_semanal": float(cuota), "semana_actual": pagos_count + 1}