# app/controllers/usuario_controller.py
from app.models.database import SessionLocal
from app.models.usuario import Usuario
from app.core.security import verificar_password
from passlib.context import CryptContext

# Configuración para encriptar las contraseñas de los nuevos cajeros
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsuarioController:
    def __init__(self):
        pass

    # ---------------------------------------------------------
    # 1. FUNCIÓN ORIGINAL INTACTA (Maneja el Login)
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. NUEVAS FUNCIONES MULTI-TENANT (Gestión de Cajeros)
    # ---------------------------------------------------------
    def obtener_usuarios_por_empresa(self, empresa_id: int):
        db = SessionLocal()
        try:
            # Filtro Multi-tenant: el Admin solo ve a los usuarios de su empresa
            usuarios = db.query(Usuario).filter(Usuario.empresa_id == empresa_id).all()
            return [{"id": u.id, "username": u.username, "rol_id": u.rol_id, "activo": u.activo} for u in usuarios]
        finally:
            db.close()

    def crear_usuario(self, empresa_id: int, username: str, password: str, rol_id: int):
        db = SessionLocal()
        try:
            # Validar que el nombre de usuario no esté tomado a nivel global
            existe = db.query(Usuario).filter(Usuario.username == username).first()
            if existe:
                return "DUPLICADO"
            
            nuevo_usuario = Usuario(
                username=username,
                password_hash=pwd_context.hash(password), # Encriptación automática
                rol_id=rol_id,
                empresa_id=empresa_id,    # Asignación automática a la empresa del Admin
                activo=True
            )
            db.add(nuevo_usuario)
            db.commit()
            return "EXITO"
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB CREAR USUARIO]: {e}")
            return "ERROR"
        finally:
            db.close()