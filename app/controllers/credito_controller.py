# app/controllers/credito_controller.py
from app.database import DatabaseConnection

class CreditoController:
    def __init__(self):
        self.db = DatabaseConnection()

    def crear_credito(self, rfc_cliente, monto, tasa_mensual, plazos):
        """Calcula el interés e inserta el crédito asociado al cliente."""
        conn = self.db.connect()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            
            # 1. Obtener el ID interno del cliente usando su RFC (Foreign Key)
            cursor.execute("SELECT id FROM clientes WHERE rfc = %s", (rfc_cliente,))
            resultado = cursor.fetchone()
            if not resultado:
                print("[ERROR] Cliente no encontrado en la base de datos.")
                return False
            cliente_id = resultado[0]

            # 2. Lógica Financiera: Interés Simple
            # Fórmula: Saldo = Monto + (Monto * (Tasa/100) * Plazos)
            interes_total = monto * (tasa_mensual / 100.0) * plazos
            saldo_restante = monto + interes_total

            # 3. Transacción SQL
            query = """
                INSERT INTO creditos (cliente_id, monto_original, tasa_interes_mensual, plazos_meses, saldo_restante)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (cliente_id, monto, tasa_mensual, plazos, saldo_restante))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"[ERROR SQL] Transacción fallida: {e}")
            return False
        finally:
            conn.close()