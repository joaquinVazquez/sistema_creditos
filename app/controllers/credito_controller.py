from datetime import date
from sqlalchemy import func
from app.models.database import SessionLocal
from app.models.credito import Credito
from app.models.clientes import Cliente
from app.models.pago import Pago
from app.models.usuario import Usuario

class CreditoController:
    def __init__(self):
        pass

    def crear_credito(self, rfc_cliente, monto, tasa_global, plazos_semanas):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc_cliente).first()
            if not cliente: return False
            
            interes_total = monto * (tasa_global / 100.0)
            saldo_inicial = monto + interes_total
            
            nuevo = Credito(
                cliente_id=cliente.id, monto_original=monto, tasa_interes_global=tasa_global,
                plazos_semanas=plazos_semanas, saldo_actual=saldo_inicial, fecha_inicio=date.today(),
                estado="ACTIVO", saldo_restante=saldo_inicial, tasa_interes_mensual=0.0,
                plazos_meses=0, fecha_otorgamiento=date.today()
            )
            db.add(nuevo)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB CREAR CREDITO]: {e}")
            return False
        finally:
            db.close()

    def obtener_historial_por_rfc(self, rfc_cliente):
        db = SessionLocal()
        try:
            creditos = db.query(Credito).join(Cliente).filter(Cliente.rfc == rfc_cliente).order_by(Credito.fecha_inicio.desc()).all()
            return [(c.id, c.fecha_inicio, c.monto_original, c.tasa_interes_global, c.plazos_semanas, c.saldo_actual, c.estado) for c in creditos]
        finally:
            db.close()

    def obtener_pagos_por_credito(self, credito_id):
        db = SessionLocal()
        try:
            pagos = db.query(Pago.id, Pago.fecha, Pago.monto, Usuario.username).join(Usuario).filter(Pago.credito_id == credito_id).order_by(Pago.fecha.desc()).all()
            return [(p.id, p.fecha, p.monto, p.username) for p in pagos]
        finally:
            db.close()

    def obtener_metricas_dashboard(self):
        """Cálculo de KPIs financieros utilizando funciones de agregación del motor SQL."""
        db = SessionLocal()
        try:
            # 1. Capital Activo
            capital = db.query(func.coalesce(func.sum(Credito.saldo_actual), 0)).filter(
                func.upper(Credito.estado) == 'ACTIVO'
            ).scalar()

            # 2. Ingresos del día de hoy
            hoy = date.today()
            ingresos = db.query(func.coalesce(func.sum(Pago.monto), 0)).filter(
                func.date(Pago.fecha) == hoy
            ).scalar()

            # 3. Clientes con crédito activo
            clientes = db.query(func.count(func.distinct(Credito.cliente_id))).filter(
                func.upper(Credito.estado) == 'ACTIVO'
            ).scalar()

            # El router debe devolver un diccionario (JSON) para la API
            return {
                "capital_activo": float(capital),
                "ingresos_hoy": float(ingresos),
                "clientes_activos": int(clientes)
            }
        except Exception as e:
            print(f"\n[ERROR ORM KPIs]: {e}\n")
            return {"capital_activo": 0.0, "ingresos_hoy": 0.0, "clientes_activos": 0}
        finally:
            db.close()