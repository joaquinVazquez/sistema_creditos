import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class DatabaseConnection:
    """Capa de acceso a datos. Gestiona la conexión a PostgreSQL."""
    
    def __init__(self):
        # Leemos las credenciales de forma segura
        self.host = os.getenv("DB_HOST", "localhost")
        self.database = os.getenv("DB_NAME", "sistema_creditos")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.port = os.getenv("DB_PORT", "5432")

    def connect(self):
        """Establece y retorna la conexión a la base de datos."""
        try:
            connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                connect_timeout=3  # NUEVO: Si en 3 segundos no conecta, lanza error
            )
            print("[SISTEMA] Conexión a PostgreSQL establecida con éxito.")
            return connection
        except OperationalError as e:
            print(f"[ERROR FATAL] No se pudo conectar a la base de datos:\n{e}")
            return None

# Bloque de prueba: Solo se ejecuta si corremos este archivo directamente
if __name__ == "__main__":
    db = DatabaseConnection()
    conn = db.connect()
    
    if conn:
        conn.close()
        print("[SISTEMA] Conexión cerrada correctamente. Listo para operar.")