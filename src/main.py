from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.config import engine, Base, SessionLocal

# Importar modelos para que SQLAlchemy los registre antes de create_all
import src.infrastructure.database.auth_models  # noqa: F401
from src.infrastructure.api.routes import router as clients_router
from src.infrastructure.api.auth_routes import auth_router
from src.application.auth_service import ensure_default_admin

# Crea las tablas (incluyendo la tabla de usuarios) si no existen
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Ámbar Rojo — Agents API",
    description="Backend con Arquitectura Hexagonal y autenticación JWT segura.",
    version="2.0.0",
)
# --- INICIO DEL HEALTH CHECK ---
@app.get("/")
@app.get("/health")  # Ruta de respaldo por si el proxy limpia la barra diagonal
def health_check():
    return {"status": "ok", "message": "API funcionando"}
# --- FIN DEL HEALTH CHECK ---
# CORS — en producción reemplaza "*" por la URL exacta del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth_router)    # /auth/login, /auth/me
app.include_router(clients_router) # /api/clients, /api/agents …


@app.on_event("startup")
def on_startup():
    """Al arrancar: crear el usuario admin por defecto si la tabla está vacía."""
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint para verificar que la API está en línea."""
    return {
        "message": "API de Ámbar Rojo activa. Visita /docs para la documentación.",
        "auth": "POST /auth/login para obtener un token JWT.",
    }
