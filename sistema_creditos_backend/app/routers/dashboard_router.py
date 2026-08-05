# app/routers/dashboard_router.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.dashboard_schema import DashboardResponse
from app.controllers.credito_controller import CreditoController
from datetime import datetime, date

# --- TUS IMPORTACIONES REALES DE BASE DE DATOS Y MODELOS ---
from app.models.database import SessionLocal
from app.models.pago import Pago
from app.models.credito import Credito
from sqlalchemy import func

# Importaciones de seguridad
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
credito_ctrl = CreditoController()

@router.get("/metricas", response_model=DashboardResponse)
def obtener_kpis(current_user: Usuario = Depends(get_current_user)):
    """Retorna los indicadores principales financieros del día (Ruta Protegida)."""
    try:
        kpis = credito_ctrl.obtener_metricas_dashboard()
        return {
            "capital_activo": kpis.get("capital_activo", 0.0),
            "ingresos_hoy": kpis.get("ingresos_hoy", 0.0),
            "clientes_activos": kpis.get("clientes_activos", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR_EN_METRICAS: {str(e)}")


@router.get("/corte-caja")
def obtener_corte_caja(fecha: date = None, current_user: Usuario = Depends(get_current_user)):
    """
    Calcula el balance diario de caja: Ingresos (Pagos) y Egresos (Créditos otorgados).
    Usa SQLAlchemy y SessionLocal para consultar la base de datos de forma segura.
    """
    if not fecha:
        fecha = datetime.now().date()
        
    db = SessionLocal()
    try:
        # 1. Calcular Ingresos (Suma de abonos en la tabla 'pagos' para la fecha)
        # Filtramos por la fecha de la transacción (asumiendo campo 'fecha' o 'created_at')
        total_ingresos = db.query(func.sum(Pago.monto))\
            .filter(func.date(Pago.fecha) == fecha)\
            .scalar()
        
        ingresos = float(total_ingresos) if total_ingresos else 0.0

        # 2. Calcular Egresos (Suma de montos prestados en la tabla 'creditos' para la fecha)
        total_egresos = db.query(func.sum(Credito.monto_prestado))\
            .filter(func.date(Credito.fecha) == fecha)\
            .scalar()
            
        egresos = float(total_egresos) if total_egresos else 0.0

        # 3. Conteo de operaciones del día
        count_pagos = db.query(Pago).filter(func.date(Pago.fecha) == fecha).count()
        count_creditos = db.query(Credito).filter(func.date(Credito.fecha) == fecha).count()

        balance_efectivo = ingresos - egresos

        return {
            "fecha": fecha.strftime("%Y-%m-%d"),
            "ingresos": ingresos,
            "egresos": egresos,
            "balance_neto": balance_efectivo,
            "total_operaciones": count_pagos + count_creditos,
            "solicitado_por": current_user.username
        }

    except Exception as e:
        print(f"[ERROR BACKEND CORTE CAJA]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al calcular corte de caja: {str(e)}")
    finally:
        db.close()