import os
import sys
import psycopg2
from dotenv import load_dotenv

# ==========================================
# TRAZADOR DE RUTAS DE ENTORNO
# ==========================================
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
    print(f"[DEBUG] Modo EXE detectado. Base path: {base_path}")
else:
    # Resolvemos la ruta: app/database.py -> app/ -> creditos_app/
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"[DEBUG] Modo Python (Desarrollo) detectado. Base path: {base_path}")

ruta_env = os.path.join(base_path, '.env')
print(f"[DEBUG] Buscando archivo .env en: {ruta_env}")
print(f"[DEBUG] ¿El archivo .env existe físicamente?: {os.path.exists(ruta_env)}")

load_dotenv(dotenv_path=ruta_env)
# ==========================================

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "creditos_db")
        
        # Validar si las credenciales se cargaron o están vacías
        if not self.password:
            print("[ALERTA] La contraseña está vacía. El .env no se está leyendo o no tiene DB_PASSWORD.")
        else:
            print(f"[DEBUG] Credenciales cargadas. Intentando conectar a: {self.database}@{self.host}")

    def connect(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except Exception as e:
            print(f"\n[ERROR CRÍTICO DB]: {e}\n")
            return None