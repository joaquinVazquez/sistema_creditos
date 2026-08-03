# app/routers/credito_router.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func # NECESARIO para el count
from typing import List
from app.schemas.credito_schema import CreditoCreate, CreditoResponse
from app.controllers.credito_controller import CreditoController
from app.core.dependencies import get_current_user, get_db # IMPORTANTE: get_db
from app.models.usuario import Usuario
from app.models.credito import Credito
from app.models.clientes import Cliente
from app.models.pago import Pago

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

@router.get("/clientes/{rfc}/creditos-activos")
def get_creditos_activos(rfc: str, db: Session = Depends(get_db)):
    """Busca créditos activos del cliente."""
    # IMPORTANTE: Asegúrate de usar .activo == True, no .is_active
    creditos = db.query(Credito).join(Cliente).filter(Cliente.rfc == rfc, Credito.estado == "ACTIVO").all()
    return creditos

@router.get("/{id_credito}/metricas")
def get_metricas(id_credito: int, db: Session = Depends(get_db)):
    """Calcula cuota semanal y semana actual."""
    credito = db.query(Credito).filter(Credito.id == id_credito).first()
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    
    # Lógica de negocio trasladada al backend
    pagos_count = db.query(func.count(Pago.id)).filter(Pago.credito_id == id_credito).scalar()
    
    deuda_total = credito.monto_original * (1 + (credito.tasa_interes_global / 100))
    cuota_semanal = deuda_total / credito.plazos_semanas
    
    return {"cuota_semanal": cuota_semanal, "semana_actual": pagos_count + 1}