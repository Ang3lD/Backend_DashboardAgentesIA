"""
Router: Global Agents (/api/agents)

Endpoints
---------
GET    /api/agents   — list all agents across all clients with client_name included
"""
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from src.infrastructure.api import schemas
from src.infrastructure.api.dependencies import get_db
from src.infrastructure.database.repositories import AgentRepositorySQL

router = APIRouter(prefix="/api/agents", tags=["Agents Global"])

@router.get("", response_model=List[schemas.GlobalAgentResponse])
def get_all_agents(db: Session = Depends(get_db)):
    """Returns a list of all agents, including their associated client_name."""
    repo = AgentRepositorySQL(db)
    agents_orm = repo.get_all()
    
    results = []
    for a in agents_orm:
        data = {
            "id": a.id,
            "client_id": a.client_id,
            "name": a.name,
            "type": a.type,
            "description": a.description,
            "workflow_id": a.workflow_id,
            "chatwoot_inbox": a.chatwoot_inbox,
            "model": a.model,
            "status": a.status,
            "created_at": a.created_at,
            "updated_at": a.updated_at,
            "client_name": a.client.name if a.client else "Desconocido"
        }
        results.append(data)
        
    return results
