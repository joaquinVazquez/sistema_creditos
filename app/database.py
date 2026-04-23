import psycopg2
import os
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "sistema_creditos")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")

    def connect(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return conn
        except psycopg2.DatabaseError as e:
            print(f"[CRITICAL ERROR] Fallo al conectar a PostgreSQL: {e}")
            return None