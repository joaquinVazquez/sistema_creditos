# app/models/database.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# ==========================================
# 1. RESOLUCIÓN DE RUTA ABSOLUTA
# ==========================================
# __file__ apunta a: sistema_creditos/app/models/database.py
# Subimos 3 niveles para llegar a la carpeta raíz: sistema_creditos/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# ==========================================
# 2. CARGA DE VARIABLES DE ENTORNO
# ==========================================
# Forzamos a python-dotenv a leer el archivo físico exacto
load_dotenv(dotenv_path=ENV_PATH)

# Leemos la variable (apuntará a Supabase si descomentaste la línea correcta)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# 3. BLINDAJE Y VALIDACIÓN
# ==========================================
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        f"CRÍTICO: No se encontró la variable DATABASE_URL.\n"
        f"Ruta donde Python está buscando el archivo: {ENV_PATH}\n"
        f"Asegúrate de que el archivo se llame '.env' y no '.env.txt'"
    )

# ==========================================
# 4. MOTOR ORM
# ==========================================
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()