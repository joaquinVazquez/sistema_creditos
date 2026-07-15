# app/controllers/usuario_controller.py
from app.models.database import SessionLocal
from app.models.usuario import Usuario
from app.core.security import verificar_password

class UsuarioController:
    def __init__(self):
        pass

    def autenticar_usuario(self, username, password):
        """
        Valida las credenciales del usuario utilizando ORM y hash criptográfico.
        Retorna el objeto Usuario si es válido, de lo contrario retorna None.
        """
        db = SessionLocal()
        try:
            # 1. Búsqueda del usuario activo mediante ORM
            usuario = db.query(Usuario).filter(
                Usuario.username == username, 
                Usuario.activo == True
            ).first()

            if not usuario:
                print(f"[AUTH FALLIDA]: El usuario '{username}' no existe o está inactivo.")
                return None

            # 2. Validación criptográfica de la contraseña
            # NOTA: Si en tu base de datos actual las contraseñas están en texto plano,
            # cambia temporalmente esta línea por: if password == usuario.password_hash:
            if verificar_password(password, usuario.password_hash):
                return usuario
            else:
                print(f"[AUTH FALLIDA]: Contraseña incorrecta para '{username}'.")
                return None

        except Exception as e:
            print(f"[ERROR ORM LOGIN]: Excepción durante autenticación: {e}")
            return None
        finally:
            db.close()