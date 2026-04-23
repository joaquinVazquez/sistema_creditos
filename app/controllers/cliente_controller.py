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

    
    def guardar_cliente(self, rfc, nombre, telefono, direccion, foto_path=None, ine_path=None):
        conn = self.db.connect()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO clientes (rfc, nombre_completo, telefono, direccion, foto_path, ine_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (rfc, nombre, telefono, direccion, foto_path, ine_path))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    def obtener_expediente(self, rfc):
        """Obtiene las rutas físicas de los documentos asociados a un cliente."""
        conn = self.db.connect()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT foto_path, ine_path FROM clientes WHERE rfc = %s", (rfc,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[ERROR SQL] No se pudo obtener el expediente: {e}")
            return None
        finally:
            conn.close()