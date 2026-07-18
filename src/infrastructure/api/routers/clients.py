"""
Router: /api/clients

Endpoints
---------
GET    /api/clients                          — list clients (optional ?status=)
GET    /api/clients/{id}                     — single client
POST   /api/clients                          — create client
PUT    /api/clients/{id}                     — update client
DELETE /api/clients/{id}                     — delete client

GET    /api/clients/{id}/agents              — agents for a client
POST   /api/clients/{id}/agents              — create agent under client
PUT    /api/clients/{id}/agents/{agent_id}   — update agent under client
DELETE /api/clients/{id}/agents/{agent_id}   — delete agent under client
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from src.infrastructure.api import schemas
from src.application.services import ClientService
from src.application.usage_service import UsageService
from src.domain.models import Client
from src.infrastructure.api.dependencies import get_client_service, get_usage_service

router = APIRouter(prefix="/api/clients", tags=["Clients"])


# ─── Clients ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[schemas.ClientResponse])
def get_clients(
    status: Optional[str] = Query(
        default=None,
        description="Filter by status: active | inactive | paused",
        enum=["active", "inactive", "paused"],
    ),
    service: ClientService = Depends(get_client_service),
):
    """Returns the list of all clients. Use ?status= to filter."""
    return service.get_clients(status=status)


@router.get("/{id}", response_model=schemas.ClientResponse)
def get_client(id: int, service: ClientService = Depends(get_client_service)):
    """Returns the details of a specific client by ID."""
    client = service.get_client(id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/{id}/usage", response_model=schemas.ClientUsageResponse)
def get_client_usage(
    id: int, 
    period: Optional[str] = None, 
    service: UsageService = Depends(get_usage_service)
):
    """Returns the usage details for a specific client. Defaults to current month (YYYY-MM)."""
    import re
    if period and not re.match(r"^\d{4}-\d{2}$", period):
        raise HTTPException(status_code=400, detail="El parámetro 'period' debe tener el formato YYYY-MM (ej. 2026-06)")

    from datetime import datetime
    if not period:
        period = datetime.now().strftime("%Y-%m")
        
    result = service.get_client_usage(id, period)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("", response_model=schemas.ClientResponse, status_code=201)
def create_client(
    client_data: schemas.ClientCreate,
    service: ClientService = Depends(get_client_service),
):
    """Creates a new client."""
    new_client = Client(
        name=client_data.name,
        slug=client_data.slug,
        plan_id=client_data.plan_id,
        status=client_data.status,
        phone=client_data.phone,
        email=client_data.email,
        contact_name=client_data.contact_name,
        start_date=client_data.start_date,
        notes=client_data.notes,
    )
    return service.create_client(new_client)


@router.put("/{id}", response_model=schemas.ClientResponse)
def update_client(
    id: int,
    client_data: schemas.ClientUpdate,
    service: ClientService = Depends(get_client_service),
):
    """Updates an existing client. Only provided fields are changed."""
    updated = service.update_client(id, client_data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated


@router.delete("/{id}", status_code=204)
def delete_client(id: int, service: ClientService = Depends(get_client_service)):
    """Deletes a specific client by ID."""
    success = service.delete_client(id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")


# ─── Agents (nested under client) ────────────────────────────────────────────

@router.get("/{id}/agents", response_model=List[schemas.AgentResponse])
def get_client_agents(id: int, service: ClientService = Depends(get_client_service)):
    """Returns all agents assigned to a specific client."""
    client = service.get_client(id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return service.get_client_agents(id)


@router.post("/{id}/agents", response_model=schemas.AgentResponse, status_code=201)
def create_agent(
    id: int,
    agent_data: schemas.AgentCreate,
    service: ClientService = Depends(get_client_service),
):
    """Creates a new agent under a specific client."""
    client = service.get_client(id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    data = agent_data.model_dump()
    return service.create_agent(id, data)


@router.put("/{id}/agents/{agent_id}", response_model=schemas.AgentResponse)
def update_agent(
    id: int,
    agent_id: int,
    agent_data: schemas.AgentUpdate,
    service: ClientService = Depends(get_client_service),
):
    """Updates an agent that belongs to the specified client."""
    updated = service.update_agent(id, agent_id, agent_data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or does not belong to this client",
        )
    return updated


@router.delete("/{id}/agents/{agent_id}", status_code=204)
def delete_agent(
    id: int,
    agent_id: int,
    service: ClientService = Depends(get_client_service),
):
    """Deletes an agent that belongs to the specified client."""
    success = service.delete_agent(id, agent_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or does not belong to this client",
        )
