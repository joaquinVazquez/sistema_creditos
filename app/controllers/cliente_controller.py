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

    
    def guardar_cliente(self, rfc, nombre, telefono, direccion):
        """Inserta un nuevo cliente en la base de datos."""
        conn = self.db.connect()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO clientes (rfc, nombre_completo, telefono, direccion)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (rfc, nombre, telefono, direccion))
            conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR SQL] No se pudo guardar: {e}")
            return False
        finally:
            conn.close()