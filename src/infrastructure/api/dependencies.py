from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.config import get_db
from src.infrastructure.database.repositories import (
    ClientRepositorySQL,
    AgentRepositorySQL,
    PaymentRepositorySQL,
    UsageLogRepositorySQL,
)
from src.application.services import ClientService, BillingService
from src.application.usage_service import UsageService
from src.application.metrics_service import MetricsService


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """
    Dependency injection for the ClientService.
    Sets up the service with its required database repositories.
    """
    client_repo = ClientRepositorySQL(db)
    agent_repo = AgentRepositorySQL(db)
    return ClientService(client_repository=client_repo, agent_repository=agent_repo)


def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    """
    Dependency injection for the BillingService.
    Sets up the service with client and payment repositories.
    """
    client_repo = ClientRepositorySQL(db)
    payment_repo = PaymentRepositorySQL(db)
    return BillingService(client_repository=client_repo, payment_repository=payment_repo)

def get_usage_service(db: Session = Depends(get_db)) -> UsageService:
    """
    Dependency injection for the UsageService.
    """
    usage_repo = UsageLogRepositorySQL(db)
    agent_repo = AgentRepositorySQL(db)
    client_repo = ClientRepositorySQL(db)
    return UsageService(usage_repo, agent_repo, client_repo)

def get_metrics_service(db: Session = Depends(get_db), billing_service: BillingService = Depends(get_billing_service)) -> MetricsService:
    """
    Dependency injection for the MetricsService.
    """
    return MetricsService(db=db, billing_service=billing_service)

