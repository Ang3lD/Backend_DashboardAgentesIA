from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.config import engine, Base, SessionLocal

# Importar todos los modelos ORM para que SQLAlchemy los registre antes de create_all
import src.infrastructure.database.auth_models  # noqa: F401
import src.infrastructure.database.repositories  # noqa: F401  (ClientModel, AgentModel, PlanModel, PaymentModel)

from src.infrastructure.api.routers.clients import router as clients_router
from src.infrastructure.api.routers.billing import router as billing_router
from src.infrastructure.api.routers.payments import router as payments_router
from src.infrastructure.api.routers.health import router as health_router
from src.infrastructure.api.routers.logs import router as logs_router
from src.infrastructure.api.auth_routes import auth_router
from src.application.auth_service import ensure_default_admin

# Crea las tablas (incluida la nueva tabla payments) si no existen
Base.metadata.create_all(bind=engine)

# ─── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ámbar Rojo — Agents API",
    description=(
        "Backend con Arquitectura Hexagonal y autenticación JWT segura.\n\n"
        "**Autenticación:** `POST /auth/login` con `username` y `password` (form-data) "
        "para obtener el Bearer token."
    ),
    version="2.1.0",
)

# CORS — en producción reemplaza \"*\" por la URL exacta del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Health check raíz (para Easypanel zero-downtime) ────────────────────────
@app.get("/", tags=["Root"])
def root():
    """Root endpoint. Visita /docs para la documentación interactiva."""
    return {
        "status": "ok",
        "message": "API de Ámbar Rojo activa. Visita /docs para la documentación.",
        "auth": "POST /auth/login para obtener un token JWT.",
    }

# ─── Registrar routers ────────────────────────────────────────────────────────
app.include_router(auth_router)     # /auth/login, /auth/me
app.include_router(clients_router)  # /api/clients, /api/clients/{id}/agents
app.include_router(billing_router)   # /api/clients/{id}/billing
app.include_router(payments_router)  # /api/clients/{id}/payments
app.include_router(health_router)   # /api/health
app.include_router(logs_router)     # /api/logs

# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Al arrancar: crear el usuario admin por defecto si la tabla está vacía."""
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()