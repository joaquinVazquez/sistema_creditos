# app/controllers/cliente_controller.py
from app.models.database import SessionLocal
from app.models.clientes import Cliente

class ClienteController:
    def __init__(self):
        # El backend no necesita token de requests, se conecta directo a la DB
        pass

    def obtener_todos(self):
        db = SessionLocal()
        try:
            # Filtramos solo los activos usando la columna correcta
            clientes = db.query(Cliente).filter(Cliente.activo == True).all()
            return [(c.rfc, c.nombre_completo, c.telefono, c.created_at) for c in clientes]
        finally:
            db.close()

    def guardar_cliente(self, rfc, nombre, telefono, direccion=None, foto_path=None, ine_path=None):
        db = SessionLocal()
        try:
            nuevo_cliente = Cliente(
                rfc=rfc,
                nombre_completo=nombre,
                telefono=telefono,
                direccion=direccion,
                foto_path=foto_path,
                ine_path=ine_path,
                activo=True
            )
            db.add(nuevo_cliente)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB GUARDAR CLIENTE]: {e}")
            return False
        finally:
            db.close()

    def obtener_expediente(self, rfc):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc, Cliente.activo == True).first()
            if cliente:
                return (cliente.foto_path, cliente.ine_path)
            return None
        finally:
            db.close()

    def eliminar_cliente(self, rfc):
        """Soft delete: solo cambia el estado activo a False"""
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc).first()
            if cliente:
                cliente.activo = False
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB ELIMINAR CLIENTE]: {e}")
            return False
        finally:
            db.close()

    def obtener_cliente_por_rfc(self, rfc):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc, Cliente.activo == True).first()
            if cliente:
                return (cliente.rfc, cliente.nombre_completo, cliente.telefono)
            return None
        finally:
            db.close()

    def actualizar_cliente(self, rfc_original, datos_nuevos):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(Cliente.rfc == rfc_original, Cliente.activo == True).first()
            if cliente:
                if 'rfc' in datos_nuevos: 
                    cliente.rfc = datos_nuevos['rfc']
                if 'nombre_completo' in datos_nuevos: 
                    cliente.nombre_completo = datos_nuevos['nombre_completo']
                if 'telefono' in datos_nuevos: 
                    cliente.telefono = datos_nuevos['telefono']
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB ACTUALIZAR CLIENTE]: {e}")
            return False
        finally:
            db.close()