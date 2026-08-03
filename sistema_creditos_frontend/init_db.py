# init_db.py
from app.models.database import engine, Base

# Importa TODOS tus modelos aquí para que 'Base' los reconozca
from app.models.usuario import Usuario
from app.models.clientes import Cliente
from app.models.credito import Credito
from app.models.pago import Pago

print("Construyendo esquema de base de datos...")
Base.metadata.create_all(engine)
print("¡Esquema creado exitosamente!")