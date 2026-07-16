# setup_admin.py
from app.models.database import SessionLocal
from app.models.usuario import Usuario
from app.core.security import obtener_password_hash

db = SessionLocal()
try:
    nuevo_admin = Usuario(
        username="admin",
        password_hash=obtener_password_hash("tu_contraseña_segura"),
        rol_id=1,
        activo=True
    )
    db.add(nuevo_admin)
    db.commit()
    print("Administrador creado en Supabase con éxito.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()