# app/routers/dashboard_router.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.dashboard_schema import DashboardResponse
from app.controllers.credito_controller import CreditoController
from datetime import datetime, date
from app.db.database import get_db

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


@router.get("/corte-caja")
def obtener_corte_caja(fecha: date = None, current_user: Usuario = Depends(get_current_user)):
    """
    Calcula el balance diario de caja: Ingresos (Pagos) y Egresos (Créditos otorgados).
    Si no se pasa fecha, toma la fecha actual del servidor.
    (Ruta Protegida por JWT).
    """
    if not fecha:
        fecha = datetime.now().date()
        
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    try:
        supabase = get_db() # Instancia de tu cliente Supabase
        
        # 1. Calcular Ingresos (Suma de abonos en la tabla 'pagos')
        pagos_response = supabase.table("pagos")\
            .select("monto")\
            .gte("created_at", f"{fecha_str}T00:00:00")\
            .lte("created_at", f"{fecha_str}T23:59:59")\
            .execute()
            
        ingresos = sum([float(pago["monto"]) for pago in pagos_response.data]) if pagos_response.data else 0.0

        # 2. Calcular Egresos (Suma de montos prestados en la tabla 'creditos')
        creditos_response = supabase.table("creditos")\
            .select("monto_prestado")\
            .gte("created_at", f"{fecha_str}T00:00:00")\
            .lte("created_at", f"{fecha_str}T23:59:59")\
            .execute()
            
        egresos = sum([float(credito["monto_prestado"]) for credito in creditos_response.data]) if creditos_response.data else 0.0

        # 3. Balance Neto
        balance_efectivo = ingresos - egresos

        return {
            "fecha": fecha_str,
            "ingresos": ingresos,
            "egresos": egresos,
            "balance_neto": balance_efectivo,
            "total_operaciones": len(pagos_response.data) + len(creditos_response.data),
            "solicitado_por": current_user.username  # Audit trail: sabemos quién pidió el corte
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular corte de caja: {str(e)}")