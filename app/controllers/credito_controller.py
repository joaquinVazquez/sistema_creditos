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
            
            # 1. Obtener el ID interno del cliente usando su RFC (Foreign Key)
            cursor.execute("SELECT id FROM clientes WHERE rfc = %s", (rfc_cliente,))
            resultado = cursor.fetchone()
            if not resultado:
                print("[ERROR] Cliente no encontrado en la base de datos.")
                return False
            cliente_id = resultado[0]

            # 2. Lógica Financiera: Interés Global Simple
            # Fórmula: Total = Monto + (Monto * (TasaGlobal / 100))
            interes_total = monto * (tasa_global / 100.0)
            saldo_restante = monto + interes_total

            # 3. Transacción SQL con los nuevos nombres de columnas (Semanales)
            query = """
                INSERT INTO creditos (cliente_id, monto_original, tasa_interes_global, plazos_semanas, saldo_restante)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (cliente_id, monto, tasa_global, plazos_semanas, saldo_restante))
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback() # Revierte cambios si algo falla en el proceso
            print(f"[ERROR SQL] Transacción fallida: {e}")
            return False
        finally:
            conn.close()

    def obtener_historial_por_rfc(self, rfc_cliente):
        """Obtiene todos los créditos históricos de un cliente."""
        conn = self.db.connect()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            # JOIN para cruzar los datos del crédito con la tabla de clientes
            query = """
                SELECT cr.id, cr.fecha_otorgamiento, cr.monto_original, 
                       cr.tasa_interes_global, cr.plazos_semanas, cr.saldo_restante, cr.estado
                FROM creditos cr
                JOIN clientes cl ON cr.cliente_id = cl.id
                WHERE cl.rfc = %s
                ORDER BY cr.fecha_otorgamiento DESC, cr.id DESC
            """
            cursor.execute(query, (rfc_cliente,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR SQL] No se pudo obtener el historial: {e}")
            return []
        finally:
            conn.close()

    def obtener_pagos_por_credito(self, credito_id):
        """Devuelve el desglose de todos los abonos realizados a un crédito específico."""
        conn = self.db.connect()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.fecha_pago, p.monto_pagado, u.username
                FROM pagos p
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.credito_id = %s
                ORDER BY p.fecha_pago DESC
            """
            cursor.execute(query, (credito_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR SQL] No se pudo obtener los abonos: {e}")
            return []
        finally:
            conn.close()