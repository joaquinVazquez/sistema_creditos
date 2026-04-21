# app/controllers/credito_controller.py
from app.database import DatabaseConnection

class CreditoController:
    def __init__(self):
        self.db = DatabaseConnection()

    def crear_credito(self, rfc_cliente, monto, tasa_global, plazos_semanas):
        """Calcula el interés global e inserta el crédito semanal."""
        conn = self.db.connect()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clientes WHERE rfc = %s", (rfc_cliente,))
            resultado = cursor.fetchone()
            if not resultado: return False
            cliente_id = resultado[0]

            # Lógica Financiera: Interés Global Simple
            # Fórmula: Total = Monto + (Monto * (TasaGlobal / 100))
            interes_total = monto * (tasa_global / 100.0)
            saldo_restante = monto + interes_total

            # Insertamos con los nuevos nombres de columnas lógicas
            query = """
                INSERT INTO creditos (cliente_id, monto_original, tasa_interes_global, plazos_semanas, saldo_restante)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (cliente_id, monto, tasa_global, plazos_semanas, saldo_restante))
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"[ERROR SQL] Transacción fallida: {e}")
            return False
        finally:
            conn.close()