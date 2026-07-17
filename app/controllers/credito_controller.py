# app/controllers/credito_controller.py
from datetime import date
from sqlalchemy import func
#from app.models.database import SessionLocal
from app.models.credito import Credito
from app.models.clientes import Cliente
from app.models.pago import Pago
from app.models.usuario import Usuario

class CreditoController:
    def __init__(self):
        # La gestión se delega a las sesiones transaccionales del ORM
        pass

    def crear_credito(self, rfc_cliente, monto, tasa_global, plazos_semanas):
        """Lógica financiera para el cálculo e inserción orientada a objetos."""
        db = SessionLocal()
        try:
            # 1. Resolución de llave foránea mediante el objeto Cliente
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc_cliente).first()
            if not cliente:
                print("[ERROR] Cliente no encontrado en la base de datos.")
                return False
            
            # 2. Cálculo financiero
            interes_total = monto * (tasa_global / 100.0)
            saldo_inicial = monto + interes_total
            
            # 3. Instanciación del modelo Crédito
            nuevo_credito = Credito(
                cliente_id=cliente.id,
                monto_original=monto,
                tasa_interes_global=tasa_global,
                plazos_semanas=plazos_semanas,
                saldo_actual=saldo_inicial,
                fecha_inicio=date.today(),
                estado="ACTIVO",
                
                # --- SATISFACCIÓN DE RESTRICCIONES NOT NULL (Legacy) ---
                saldo_restante=saldo_inicial,     # Espejo del saldo actual
                tasa_interes_mensual=0.0,         # Valor neutral inofensivo
                plazos_meses=0,                   # Valor neutral inofensivo
                fecha_otorgamiento=date.today()   # Espejo de la fecha actual
            )
            db.add(nuevo_credito)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"\n[ERROR ORM AL CREAR CRÉDITO]: {e}\n")
            return False
        finally:
            db.close()

    def obtener_historial_por_rfc(self, rfc_cliente):
        """Uso de JOIN en SQLAlchemy para extraer el historial sin romper la vista PyQt6."""
        db = SessionLocal()
        try:
            # JOIN implícito relacional filtrado por RFC
            creditos = (db.query(Credito)
                        .join(Cliente, Credito.cliente_id == Cliente.id)
                        .filter(Cliente.rfc == rfc_cliente)
                        .order_by(Credito.fecha_inicio.desc(), Credito.id.desc())
                        .all())
            
            # Mapeo a lista de tuplas para retrocompatibilidad con la GUI
            return [(c.id, c.fecha_inicio, c.monto_original, c.tasa_interes_global, 
                     c.plazos_semanas, c.saldo_actual, c.estado) for c in creditos]
        except Exception as e:
            print(f"[ERROR ORM LECTURA HISTORIAL]: {e}")
            return []
        finally:
            db.close()

    def obtener_pagos_por_credito(self, credito_id):
        """Extracción de la sábana de abonos resolviendo el nombre del cajero (Usuario)."""
        db = SessionLocal()
        try:
            # Extracción selectiva de columnas cruzando la tabla Pagos y Usuarios
            pagos = (db.query(Pago.id, Pago.fecha, Pago.monto, Usuario.username)
                     .join(Usuario, Pago.usuario_id == Usuario.id)
                     .filter(Pago.credito_id == credito_id)
                     .order_by(Pago.fecha.desc())
                     .all())
            
            # Retorna una lista de tuplas directas
            return [(p.id, p.fecha, p.monto, p.username) for p in pagos]
        except Exception as e:
            print(f"[ERROR ORM LECTURA ABONOS]: {e}")
            return []
        finally:
            db.close()

    def obtener_metricas_dashboard(self):
        """Cálculo de KPIs financieros utilizando funciones de agregación del motor SQL."""
        db = SessionLocal()
        try:
            # 1. Capital Activo (COALESCE para evitar nulos si no hay créditos)
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
            
            return (float(capital), float(ingresos), int(clientes))
            
        except Exception as e:
            print(f"\n[ERROR ORM KPIs]: {e}\n")
            return (0.0, 0.0, 0)
        finally:
            db.close()

    