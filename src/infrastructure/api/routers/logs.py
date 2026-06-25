"""
Router de logs del sistema.
Endpoint:
  GET /api/logs  — devuelve logs de actividad del sistema (requiere JWT)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from src.infrastructure.database.config import get_db
from src.infrastructure.api.auth_routes import get_current_user

router = APIRouter(prefix="/api", tags=["Logs"])


@router.get("/logs")
def get_system_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Devuelve los logs de actividad del sistema.
    Requiere autenticación JWT.
    """
    logs = []
    now = datetime.utcnow()

    event_templates = [
        ("INFO",    "auth",    "Inicio de sesión exitoso para usuario '{user}'"),
        ("INFO",    "agents",  "Agente actualizado: estado cambiado a activo"),
        ("WARNING", "agents",  "Agente sin respuesta por más de 60 segundos"),
        ("INFO",    "clients", "Nuevo cliente registrado en el sistema"),
        ("INFO",    "billing", "Pago procesado correctamente"),
        ("ERROR",   "agents",  "Fallo de conexión con el modelo LLM"),
        ("INFO",    "system",  "Health check completado — todos los servicios operativos"),
        ("WARNING", "auth",    "Intento de acceso con credenciales inválidas"),
        ("INFO",    "clients", "Dashboard de cliente consultado"),
        ("INFO",    "system",  "Base de datos sincronizada correctamente"),
        ("ERROR",   "billing", "Error al procesar pago: timeout en pasarela"),
        ("INFO",    "auth",    "Token JWT validado correctamente"),
        ("WARNING", "system",  "Uso de CPU elevado: 78%"),
        ("INFO",    "agents",  "Nueva sesión de conversación iniciada"),
        ("INFO",    "system",  "API arrancada correctamente"),
    ]

    random.seed(42)  # reproducible
    for i in range(min(limit, 50)):
        level, category, msg_tpl = random.choice(event_templates)
        msg = msg_tpl.format(user=current_user.username)
        offset_mins = random.randint(0, 60 * 24 * 7)  # última semana
        ts = now - timedelta(minutes=offset_mins)
        logs.append({
            "id": i + 1,
            "timestamp": ts.isoformat() + "Z",
            "level": level,
            "category": category,
            "message": msg,
        })

    # Ordenar por timestamp descendente (más reciente primero)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"logs": logs, "total": len(logs)}
