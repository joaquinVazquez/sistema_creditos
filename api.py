# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cliente_router, credito_router

# Inicialización de la aplicación
app = FastAPI(
    title="Sistema de Créditos API",
    description="Backend transaccional para gestión de cartera y cobranza",
    version="2.0.0"
)

# Configuración CORS para permitir consumo desde web o herramientas externas (n8n, React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Integración de Módulos (Routers)
app.include_router(cliente_router.router)
app.include_router(credito_router.router)

@app.get("/")
def health_check():
    return {"status": "ok", "sistema": "API de Créditos Operativa"}