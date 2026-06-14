from app.database import DatabaseConnection

class PagoController:
    def __init__(self):
        # Inicialización del pool o clase de conexión
        self.db = DatabaseConnection()

    def obtener_creditos_cliente(self, rfc):
        """Busca créditos activos del cliente usando su RFC (vía JOIN)."""
        conn = self.db.connect()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT c.id, c.monto_original, c.saldo_actual, c.estado, c.fecha_inicio
                FROM creditos c
                JOIN clientes cl ON c.cliente_id = cl.id
                WHERE cl.rfc = %s AND c.estado = 'ACTIVO'
                ORDER BY c.fecha_inicio DESC
            """
            cursor.execute(query, (rfc,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ERROR SQL] Al obtener créditos por RFC: {e}")
            return []
        finally:
            conn.close()

    def registrar_pago(self, id_credito, usuario_id, monto_abono):
        """Registra el abono en la tabla pagos y decrementa el saldo_actual del crédito."""
        conn = self.db.connect()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            
            # 1. Inserción del registro de pago
            query_pago = """
                INSERT INTO pagos (credito_id, usuario_id, monto, fecha)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(query_pago, (id_credito, usuario_id, monto_abono))
            
            # 2. Actualización del saldo en la tabla créditos
            query_update = """
                UPDATE creditos 
                SET saldo_actual = saldo_actual - %s 
                WHERE id = %s
            """
            cursor.execute(query_update, (monto_abono, id_credito))
            
            # 3. Validar si el crédito se liquidó por completo para cambiar su estado
            query_check = "SELECT saldo_actual FROM creditos WHERE id = %s"
            cursor.execute(query_check, (id_credito,))
            saldo_restante = cursor.fetchone()[0]
            
            if saldo_restante <= 0:
                query_liquidar = "UPDATE creditos SET estado = 'PAGADO' WHERE id = %s"
                cursor.execute(query_liquidar, (id_credito,))

            conn.commit()
            return True
        except Exception as e:
            print(f"\n[ERROR SQL] Transacción fallida al registrar pago: {e}\n")
            conn.rollback()
            return False
        finally:
            conn.close()

    def obtener_metricas_cobro(self, id_credito):
        """Calcula la cuota matemática y la semana actual de un crédito activo."""
        conn = self.db.connect()
        if not conn: 
            return 0.0, 1
        
        try:
            cursor = conn.cursor()
            # 1. Traer condiciones iniciales del crédito
            query_credito = """
                SELECT monto_original, tasa_interes_global, plazos_semanas
                FROM creditos WHERE id = %s
            """
            cursor.execute(query_credito, (id_credito,))
            credito = cursor.fetchone()
            
            # 2. Contar cuántos pagos históricos se han procesado para este crédito
            query_pagos = "SELECT COUNT(*) FROM pagos WHERE credito_id = %s"
            cursor.execute(query_pagos, (id_credito,))
            pagos_realizados = cursor.fetchone()[0]
            
            if credito:
                monto, tasa, plazos = credito
                monto = float(monto or 0)
                tasa = float(tasa or 0)
                plazos = int(plazos or 1)
                
                # Fórmula de interés simple: Total = Capital * (1 + (Tasa/100))
                deuda_total = monto * (1 + (tasa / 100))
                cuota_semanal = deuda_total / plazos
                semana_actual = pagos_realizados + 1
                
                return cuota_semanal, semana_actual
                
            return 0.0, 1
        except Exception as e:
            print(f"\n[ERROR MATEMÁTICAS COBRO]: {e}\n")
            return 0.0, 1
        finally:
            conn.close()