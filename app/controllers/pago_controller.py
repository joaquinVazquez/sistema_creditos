from app.database import DatabaseConnection

class PagoController:
    def __init__(self):
        self.db = DatabaseConnection()

    def registrar_pago(self, credito_id, usuario_id, monto_abono):
        """Registra el abono y actualiza el saldo del crédito en una sola transacción."""
        conn = self.db.connect()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            
            # 1. Verificar saldo actual antes de proceder
            cursor.execute("SELECT saldo_restante FROM creditos WHERE id = %s", (credito_id,))
            saldo_actual = cursor.fetchone()[0]
            
            if monto_abono > saldo_actual:
                print("[ERROR] El abono excede el saldo pendiente.")
                return False

            # 2. Insertar el registro de pago
            cursor.execute(
                "INSERT INTO pagos (credito_id, usuario_id, monto_pagado) VALUES (%s, %s, %s)",
                (credito_id, usuario_id, monto_abono)
            )

            # 3. Actualizar el saldo en la tabla de créditos
            cursor.execute(
                "UPDATE creditos SET saldo_restante = saldo_restante - %s WHERE id = %s",
                (monto_abono, credito_id)
            )
            
            # 4. Si todo salió bien, consolidar cambios
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback() # Si falla, deshacer todo
            print(f"[ERROR SQL] Error en transacción de pago: {e}")
            return False
        finally:
            conn.close()

    def obtener_creditos_cliente(self, rfc_cliente):
        """Retorna los créditos activos de un cliente específico."""
        conn = self.db.connect()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT cr.id, cr.monto_original, cr.saldo_restante, cr.estado, cr.fecha_otorgamiento 
                FROM creditos cr
                JOIN clientes cl ON cr.cliente_id = cl.id
                WHERE cl.rfc = %s AND cr.saldo_restante > 0
            """
            cursor.execute(query, (rfc_cliente,))
            return cursor.fetchall()
        finally:
            conn.close()