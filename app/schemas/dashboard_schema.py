# app/schemas/dashboard_schema.py
from pydantic import BaseModel

class DashboardResponse(BaseModel):
    capital_activo: float
    ingresos_hoy: float
    clientes_activos: int