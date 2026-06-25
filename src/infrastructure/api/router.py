from fastapi import APIRouter
from src.infrastructure.api.routers import clients, health, billing

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(clients.router)
api_router.include_router(billing.router)
