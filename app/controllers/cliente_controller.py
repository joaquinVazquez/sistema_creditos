# app/controllers/cliente_controller.py
from app.database import DatabaseConnection

class ClienteController:
    def __init__(self):
        self.db = DatabaseConnection()

    def obtener_todos(self):
        """Retorna una lista de tuplas con los clientes activos."""
        conn = self.db.connect()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT rfc, nombre_completo, telefono, fecha_registro FROM clientes ORDER BY id DESC")
            resultados = cursor.fetchall()
            return resultados
        except Exception as e:
            print(f"[ERROR SQL] {e}")
            return []
        finally:
            conn.close()