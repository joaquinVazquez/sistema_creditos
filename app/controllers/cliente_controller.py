# app/controllers/cliente_controller.py
from app.models.database import SessionLocal
from app.models.clientes import Cliente

class ClienteController:
    def __init__(self):
        # Se elimina la dependencia de la conexión SQL cruda. La sesión se gestiona por método.
        pass

    def obtener_todos(self):
        """Retorna una lista de tuplas con los clientes activos (ORM)."""
        db = SessionLocal()
        try:
            # Filtro exclusivo de clientes activos (Soft Delete aplicado)
            clientes = db.query(Cliente).filter(Cliente.is_active == True).order_by(Cliente.id.desc()).all()

            # Compatibilidad inversa con PyQt6: devolvemos tuplas.
            # Mapeamos 'created_at' en reemplazo del antiguo 'fecha_registro'
            return [(c.rfc, c.nombre_completo, c.telefono, c.created_at) for c in clientes]
        except Exception as e:
            print(f"[ERROR ORM LECTURA]: {e}")
            return []
        finally:
            db.close()

    def guardar_cliente(self, rfc, nombre, telefono, direccion=None, foto_path=None, ine_path=None):
        """Inserta un nuevo cliente incluyendo rutas de expediente físico."""
        db = SessionLocal()
        try:
            nuevo_cliente = Cliente(
                rfc=rfc,
                nombre_completo=nombre,
                telefono=telefono,
                direccion=direccion,
                foto_path=foto_path,
                ine_path=ine_path
            )
            db.add(nuevo_cliente)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"\n[ERROR CRÍTICO AL GUARDAR CLIENTE]: {e}\n")
            return False
        finally:
            db.close()

    def obtener_expediente(self, rfc):
        """Obtiene las rutas físicas de los documentos asociados a un cliente."""
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc, Cliente.is_active == True).first()
            if cliente:
                # getattr() previene colapsos si las columnas aún no existen en el modelo de SQLAlchemy
                return (getattr(cliente, 'foto_path', None), getattr(cliente, 'ine_path', None))
            return None
        except Exception as e:
            print(f"[ERROR ORM LECTURA EXPEDIENTE]: {e}")
            return None
        finally:
            db.close()

    def eliminar_cliente(self, rfc):
        """
        Transición a Baja Lógica (Soft Delete).
        En lugar de destruir el registro (DELETE) y violar la integridad referencial,
        se apaga la bandera is_active para auditoría.
        """
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc).first()
            if not cliente:
                return False

            cliente.is_active = False
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"\n[ERROR CRÍTICO AL ELIMINAR CLIENTE (SOFT DELETE)]: {e}\n")
            return False
        finally:
            db.close()

    def obtener_cliente_por_rfc(self, rfc):
        """Extrae el registro completo para prellenar el formulario."""
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc, Cliente.is_active == True).first()
            if cliente:
                return (cliente.rfc, cliente.nombre_completo, cliente.telefono)
            return None
        except Exception as e:
            print(f"\n[ERROR ORM LECTURA CLIENTE]: {e}\n")
            return None
        finally:
            db.close()

    def actualizar_cliente(self, rfc_original, datos_nuevos):
        """Sobrescribe los datos mediante la sesión transaccional."""
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc_original).first()
            if not cliente:
                return False

            cliente.rfc = datos_nuevos.get('rfc', cliente.rfc)
            cliente.nombre_completo = datos_nuevos.get('nombre', cliente.nombre_completo)
            cliente.telefono = datos_nuevos.get('telefono', cliente.telefono)

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"\n[ERROR ORM UPDATE]: {e}\n")
            return False
        finally:
            db.close()