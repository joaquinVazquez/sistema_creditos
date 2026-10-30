from app.models.database import SessionLocal
from app.models.clientes import Cliente
from app.models.credito import Credito
from app.models.pago import Pago

def rescatar_datos_antiguos():
    db = SessionLocal()
    try:
        # 1. Actualizar Clientes sin empresa
        clientes_act = db.query(Cliente).filter(Cliente.empresa_id == None).update({"empresa_id": 1})
        
        # 2. Actualizar Créditos sin empresa
        creditos_act = db.query(Credito).filter(Credito.empresa_id == None).update({"empresa_id": 1})
        
        # 3. Actualizar Pagos sin empresa
        pagos_act = db.query(Pago).filter(Pago.empresa_id == None).update({"empresa_id": 1})
        
        db.commit()
        print(f"Éxito: Se vincularon {clientes_act} clientes, {creditos_act} créditos y {pagos_act} pagos a la Empresa 1.")
    except Exception as e:
        db.rollback()
        print(f"Error al actualizar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    rescatar_datos_antiguos()