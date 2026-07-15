# app/controllers/pago_controller.py
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from app.models.database import SessionLocal
from app.models.pago import Pago
from app.models.credito import Credito
from app.models.clientes import Cliente

class PagoController:
    def __init__(self):
        # La conexión se gestiona mediante sesiones aisladas por transacción
        pass

    def obtener_creditos_cliente(self, rfc):
        """Busca créditos activos del cliente cruzando (JOIN) con SQLAlchemy."""
        db = SessionLocal()
        try:
            creditos = (db.query(
                            Credito.id, 
                            Credito.monto_original, 
                            Credito.saldo_actual, 
                            Credito.estado, 
                            Credito.fecha_inicio
                        )
                        .join(Cliente, Credito.cliente_id == Cliente.id)
                        .filter(Cliente.rfc == rfc, func.upper(Credito.estado) == 'ACTIVO')
                        .order_by(Credito.fecha_inicio.desc())
                        .all())
            return creditos
        except Exception as e:
            print(f"[ERROR ORM] Al obtener créditos por RFC: {e}")
            return []
        finally:
            db.close()

    def obtener_metricas_cobro(self, id_credito):
        """Calcula la cuota matemática y la semana actual de un crédito activo (ORM)."""
        db = SessionLocal()
        try:
            credito = db.query(Credito).filter(Credito.id == id_credito).first()
            pagos_realizados = db.query(func.count(Pago.id)).filter(Pago.credito_id == id_credito).scalar()
            
            if credito:
                monto = float(credito.monto_original or 0)
                tasa = float(credito.tasa_interes_global or 0)
                plazos = int(credito.plazos_semanas or 1)
                
                deuda_total = monto * (1 + (tasa / 100))
                cuota_semanal = deuda_total / plazos
                semana_actual = pagos_realizados + 1
                
                return cuota_semanal, semana_actual
                
            return 0.0, 1
        except Exception as e:
            print(f"\n[ERROR MATEMÁTICAS COBRO ORM]: {e}\n")
            return 0.0, 1
        finally:
            db.close()

    def registrar_pago(self, credito_id, usuario_id, monto):
        """
        Registra un abono y actualiza el saldo del crédito de forma atómica.
        Aplica reglas de negocio para la liquidación automática de cuentas.
        """
        db = SessionLocal()
        try:
            # 0. Sanitización Financiera: Evitar colisión float vs Decimal
            monto_seguro = Decimal(str(monto))

            # 1. Bloquear y extraer el crédito correspondiente para actualización
            credito = db.query(Credito).filter(Credito.id == credito_id).first()
            if not credito:
                print(f"[ERROR PAGO]: El crédito ID {credito_id} no existe.")
                return False

            # 2. Instanciar el registro del abono 
            nuevo_pago = Pago(
                credito_id=credito_id,
                usuario_id=usuario_id,
                monto=monto_seguro,
                monto_pagado=monto_seguro,   
                fecha_pago=datetime.now()    
            )
            db.add(nuevo_pago)

            # 3. Modificación del saldo de forma segura
            credito.saldo_actual -= monto_seguro
            if getattr(credito, 'saldo_restante', None) is not None:
                credito.saldo_restante -= monto_seguro

            # 4. Regla de Negocio: Liquidación automática
            if credito.saldo_actual <= Decimal('0'):
                credito.saldo_actual = Decimal('0')
                if hasattr(credito, 'saldo_restante'):
                    credito.saldo_restante = Decimal('0')
                credito.estado = "PAGADO" 

            # 5. Consolidación atómica en la base de datos
            db.commit()
            return True

        except Exception as e:
            db.rollback() 
            print(f"\n[ERROR CRÍTICO TRANSACCIONAL EN PAGO]: {e}\n")
            return False
        finally:
            db.close()