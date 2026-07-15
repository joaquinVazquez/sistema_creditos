# app/routers/dashboard_router.py
from fastapi import APIRouter, HTTPException
from app.schemas.dashboard_schema import DashboardResponse
from app.controllers.credito_controller import CreditoController

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
credito_ctrl = CreditoController()

@router.get("/metricas", response_model=DashboardResponse)
def obtener_kpis():
    """Retorna los indicadores principales financieros del día."""
    try:
        # El controlador retorna una tupla: (capital, ingresos, clientes)
        kpis = credito_ctrl.obtener_metricas_dashboard()
        return {
            "capital_activo": kpis[0],
            "ingresos_hoy": kpis[1],
            "clientes_activos": kpis[2]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))