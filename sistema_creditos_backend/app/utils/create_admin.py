# app/utils/create_admin.py
import sys
import os
import bcrypt

# Añadir el directorio raíz al path para poder importar nuestra base de datos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.database import DatabaseConnection

def crear_usuario_admin():
    db = DatabaseConnection()
    conn = db.connect()
    if not conn:
        return

    # Contraseña en texto plano que el admin escribirá
    password_plana = "admin123"
    # Generamos el hash criptográfico
    password_hash = bcrypt.hashpw(password_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        cursor = conn.cursor()
        # Insertamos el usuario con rol 1 (ADMIN, que creamos en el Sprint 1)
        cursor.execute(
            """
            INSERT INTO usuarios (rol_id, username, password_hash) 
            VALUES (1, 'admin', %s)
            ON CONFLICT (username) DO NOTHING;
            """, 
            (password_hash,)
        )
        conn.commit()
        print("[SISTEMA] Usuario 'admin' creado/verificado con éxito. Contraseña temporal: admin123")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el usuario: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    crear_usuario_admin()