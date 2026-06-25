from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.infrastructure.api import schemas
from src.application.services import ClientService
from src.domain.models import Client
from src.infrastructure.api.dependencies import get_client_service

router = APIRouter(prefix="/api/clients", tags=["Clients"])

@router.get("", response_model=List[schemas.ClientResponse])
def get_clients(service: ClientService = Depends(get_client_service)):
    """Retrieves the list of all clients."""
    return service.get_clients()

@router.get("/{id}", response_model=schemas.ClientResponse)
def get_client(id: int, service: ClientService = Depends(get_client_service)):
    """Retrieves the details of a specific client by ID."""
    client = service.get_client(id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("", response_model=schemas.ClientResponse)
def create_client(client_data: schemas.ClientCreate, service: ClientService = Depends(get_client_service)):
    """Creates a new client in the system."""
    new_client_domain = Client(
        name=client_data.name,
        slug=client_data.slug,
        plan_id=client_data.plan_id,
        status=client_data.status,
        start_date=client_data.start_date,
        notes=client_data.notes
    )
    return service.create_client(new_client_domain)

@router.get("/{id}/agents", response_model=List[schemas.AgentResponse])
def get_client_agents(id: int, service: ClientService = Depends(get_client_service)):
    """Retrieves all agents assigned to a specific client."""
    client = service.get_client(id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return service.get_client_agents(id)

@router.get("/api/clients/{id}/dashboard", response_model=schemas.ClientDashboardResponse, tags=["Clients"])
def get_client_dashboard(id: int, days: int = 30, service: ClientService = Depends(get_client_service)):
    """Retrieves the full dashboard metrics and overview for a specific client."""
    dashboard_data = service.get_client_dashboard(id, days)
    if not dashboard_data:
        raise HTTPException(status_code=404, detail="Client not found")
    return dashboard_data
