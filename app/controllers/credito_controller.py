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
            
            # 1. Obtener el ID interno del cliente
            cursor.execute("SELECT id FROM clientes WHERE rfc = %s", (rfc_cliente,))
            resultado = cursor.fetchone()
            if not resultado:
                print("[ERROR] Cliente no encontrado en la base de datos.")
                return False
            cliente_id = resultado[0]

            # 2. Lógica Financiera: Interés Global Simple
            interes_total = monto * (tasa_global / 100.0)
            saldo_inicial = monto + interes_total

            # 3. Transacción SQL sincronizada al nuevo esquema (saldo_actual y fecha_inicio)
            query = """
                INSERT INTO creditos (cliente_id, monto_original, tasa_interes_global, plazos_semanas, saldo_actual, fecha_inicio)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            """
            cursor.execute(query, (cliente_id, monto, tasa_global, plazos_semanas, saldo_inicial))
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"[ERROR SQL] Transacción fallida en crear_credito: {e}")
            return False
        finally:
            conn.close()

    def obtener_historial_por_rfc(self, rfc_cliente):
        """Obtiene todos los créditos históricos de un cliente."""
        conn = self.db.connect()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            # Sincronizado a cr.fecha_inicio y cr.saldo_actual
            query = """
                SELECT cr.id, cr.fecha_inicio, cr.monto_original, 
                       cr.tasa_interes_global, cr.plazos_semanas, cr.saldo_actual, cr.estado
                FROM creditos cr
                JOIN clientes cl ON cr.cliente_id = cl.id
                WHERE cl.rfc = %s
                ORDER BY cr.fecha_inicio DESC, cr.id DESC
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
            # Sincronizado a p.fecha y p.monto
            query = """
                SELECT p.id, p.fecha, p.monto, u.username
                FROM pagos p
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.credito_id = %s
                ORDER BY p.fecha DESC
            """
            cursor.execute(query, (credito_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR SQL] No se pudo obtener los abonos: {e}")
            return []
        finally:
            conn.close()

    def obtener_metricas_dashboard(self):
        """Calcula los KPIs usando el esquema exacto de la base de datos."""
        conn = self.db.connect()
        if not conn: return (0, 0, 0)
        try:
            cursor = conn.cursor()
            
            # Sincronizado a saldo_actual
            cursor.execute("SELECT COALESCE(SUM(saldo_actual), 0) FROM creditos WHERE UPPER(estado) = 'ACTIVO'")
            capital = cursor.fetchone()[0]
            
            # Sincronizado a monto y fecha
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM pagos WHERE fecha = CURRENT_DATE")
            ingresos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT cliente_id) FROM creditos WHERE UPPER(estado) = 'ACTIVO'")
            clientes = cursor.fetchone()[0]
            
            return (float(capital), float(ingresos), int(clientes))
            
        except Exception as e:
            print(f"\n[ERROR EN SQL DE KPIs]: {e}\n")
            return (0, 0, 0)
        finally:
            conn.close()