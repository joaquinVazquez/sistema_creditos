# app/routers/dashboard_router.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.dashboard_schema import DashboardResponse
from app.controllers.credito_controller import CreditoController

# Importaciones de seguridad
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
credito_ctrl = CreditoController()

@router.get("/metricas", response_model=DashboardResponse)
def obtener_kpis(current_user: Usuario = Depends(get_current_user)):
    """Retorna los indicadores principales financieros del día (Ruta Protegida)."""
    try:
        # Aquí recibimos un DICCIONARIO, no una lista.
        kpis = credito_ctrl.obtener_metricas_dashboard()
        
        # Accedemos mediante las llaves del diccionario
        return {
            "capital_activo": kpis.get("capital_activo", 0.0),
            "ingresos_hoy": kpis.get("ingresos_hoy", 0.0),
            "clientes_activos": kpis.get("clientes_activos", 0)
        }
    except Exception as e:
        # Esto te dirá exactamente el error si algo más falla
        raise HTTPException(status_code=500, detail=f"ERROR_EN_METRICAS: {str(e)}")