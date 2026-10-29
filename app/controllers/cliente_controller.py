# app/controllers/cliente_controller.py
from datetime import date
from sqlalchemy import func
from app.models.database import SessionLocal
from app.models.clientes import Cliente
from app.models.credito import Credito 
from app.models.pago import Pago       

class ClienteController:
    def __init__(self):
        pass

    def obtener_todos(self, empresa_id: int, skip: int = 0, limit: int = 100, incluir_inactivos: bool = False):
        db = SessionLocal()
        try:
            # FILTRO MULTI-TENANT OBLIGATORIO
            query = db.query(Cliente).filter(Cliente.empresa_id == empresa_id)
            
            if not incluir_inactivos:
                query = query.filter(Cliente.activo == True)
                
            clientes = query.order_by(Cliente.id.desc()).offset(skip).limit(limit).all()
            
            return [(c.rfc, c.nombre_completo, c.telefono, c.created_at, c.activo) for c in clientes]
        except Exception as e:
            print(f"[ERROR DB OBTENER CLIENTES]: {e}")
            return []
        finally:
            db.close()

    def guardar_cliente(self, empresa_id: int, rfc, nombre, telefono, direccion=None, foto_path=None, ine_path=None):
        db = SessionLocal()
        try:
            # 1. Verificar si el RFC ya existe EN ESTA EMPRESA
            cliente_existente = db.query(Cliente).filter(
                Cliente.empresa_id == empresa_id, 
                Cliente.rfc == rfc
            ).first()
            
            if cliente_existente:
                return "DUPLICADO"

            # 2. Si no existe, procedemos a guardarlo asociado a la empresa
            nuevo_cliente = Cliente(
                empresa_id=empresa_id, # ASIGNACIÓN MULTI-TENANT
                rfc=rfc,
                nombre_completo=nombre,
                telefono=telefono,
                direccion=direccion,
                foto_path=foto_path,
                ine_path=ine_path
            )
            db.add(nuevo_cliente)
            db.commit()
            return "EXITO"
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB GUARDAR CLIENTE]: {e}")
            return "ERROR"
        finally:
            db.close()

    def obtener_expediente(self, empresa_id: int, rfc):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(
                Cliente.empresa_id == empresa_id, 
                Cliente.rfc == rfc
            ).first()
            if cliente:
                return (cliente.foto_path, cliente.ine_path)
            return None
        finally:
            db.close()

    def archivar_cliente(self, empresa_id: int, rfc: str) -> bool:
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(
                Cliente.empresa_id == empresa_id, 
                Cliente.rfc == rfc
            ).first()
            
            if not cliente:
                return False
            
            cliente.activo = False
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB ARCHIVAR CLIENTE]: {e}")
            return False
        finally:
            db.close()

    def desarchivar_cliente(self, empresa_id: int, rfc: str) -> bool:
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(
                Cliente.empresa_id == empresa_id, 
                Cliente.rfc == rfc
            ).first()
            
            if not cliente:
                return False
            
            cliente.activo = True
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB DESARCHIVAR CLIENTE]: {e}")
            return False
        finally:
            db.close()

    def obtener_cliente_por_rfc(self, empresa_id: int, rfc):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(
                Cliente.empresa_id == empresa_id, 
                Cliente.rfc == rfc
            ).first()
            
            if cliente:
                return {
                    "rfc": cliente.rfc,
                    "nombre_completo": cliente.nombre_completo,
                    "telefono": cliente.telefono,
                    "direccion": getattr(cliente, 'direccion', None),
                    "foto_path": getattr(cliente, 'foto_path', None),
                    "ine_path": getattr(cliente, 'ine_path', None)
                }
            return None
        finally:
            db.close()

    def actualizar_cliente(self, empresa_id: int, rfc_original, datos_nuevos):
        db = SessionLocal()
        try:
            cliente = db.query(Cliente).filter(
                Cliente.empresa_id == empresa_id, 
                Cliente.rfc == rfc_original
            ).first()
            
            if cliente:
                if 'rfc' in datos_nuevos: cliente.rfc = datos_nuevos['rfc']
                if 'nombre_completo' in datos_nuevos: cliente.nombre_completo = datos_nuevos['nombre_completo']
                if 'telefono' in datos_nuevos: cliente.telefono = datos_nuevos['telefono']
                if 'direccion' in datos_nuevos: cliente.direccion = datos_nuevos['direccion']
                if 'foto_path' in datos_nuevos: cliente.foto_path = datos_nuevos['foto_path']
                if 'ine_path' in datos_nuevos: cliente.ine_path = datos_nuevos['ine_path']
                
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"[ERROR DB ACTUALIZAR CLIENTE]: {e}")
            return False
        finally:
            db.close()