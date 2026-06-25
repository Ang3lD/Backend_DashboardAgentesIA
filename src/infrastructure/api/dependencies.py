from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.config import get_db
from src.infrastructure.database.repositories import ClientRepositorySQL, AgentRepositorySQL
from src.application.services import ClientService

def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """
    Dependency injection for the ClientService.
    Sets up the service with its required database repositories.
    """
    client_repo = ClientRepositorySQL(db)
    agent_repo = AgentRepositorySQL(db)
    return ClientService(client_repository=client_repo, agent_repository=agent_repo)
