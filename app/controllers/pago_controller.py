from datetime import datetime
from decimal import Decimal
from app.models.database import SessionLocal
from app.models.pago import Pago
from app.models.credito import Credito

class PagoController:
    def __init__(self):
        pass

    def registrar_pago(self, credito_id, usuario_id, monto):
        db = SessionLocal()
        try:
            monto_seguro = Decimal(str(monto))
            credito = db.query(Credito).filter(Credito.id == credito_id).first()
            if not credito: return False
            
            nuevo_pago = Pago(
                credito_id=credito_id, usuario_id=usuario_id, 
                monto=monto_seguro, monto_pagado=monto_seguro, fecha_pago=datetime.now()
            )
            db.add(nuevo_pago)
            
            credito.saldo_actual -= monto_seguro
            if getattr(credito, 'saldo_restante', None) is not None:
                credito.saldo_restante -= monto_seguro
                
            if credito.saldo_actual <= Decimal('0'):
                credito.saldo_actual = Decimal('0')
                if hasattr(credito, 'saldo_restante'): credito.saldo_restante = Decimal('0')
                credito.estado = "PAGADO"
                
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB PAGO]: {e}")
            return False
        finally:
            db.close()

    def revertir_pago(self, pago_id):
        """Revierte un pago erróneo, restaura el saldo del crédito y lo reactiva si estaba pagado."""
        db = SessionLocal()
        try:
            pago = db.query(Pago).filter(Pago.id == pago_id).first()
            if not pago: 
                return False
            
            credito = db.query(Credito).filter(Credito.id == pago.credito_id).first()
            if not credito: 
                return False
            
            # 1. Devolvemos el dinero al saldo actual y restante
            credito.saldo_actual += pago.monto
            if hasattr(credito, 'saldo_restante') and getattr(credito, 'saldo_restante', None) is not None:
                credito.saldo_restante += pago.monto
            
            # 2. Si el crédito se había marcado como PAGADO por error, lo regresamos a ACTIVO
            if credito.estado == "PAGADO":
                credito.estado = "ACTIVO"
                
            # 3. Eliminamos el registro erróneo del historial
            db.delete(pago)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB REVERTIR PAGO]: {e}")
            return False
        finally:
            db.close()