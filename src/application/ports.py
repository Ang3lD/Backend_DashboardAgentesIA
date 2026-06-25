from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import Client, Agent, Payment

# Ports: Interfaces defining how the application interacts with external systems.
# The concrete implementations will reside in the infrastructure layer.

class ClientRepositoryPort(ABC):
    """Interface for Client repository operations."""

    @abstractmethod
    def get_all(self, status: Optional[str] = None) -> List[Client]:
        pass

    @abstractmethod
    def get_by_id(self, client_id: int) -> Optional[Client]:
        pass

    @abstractmethod
    def save(self, client: Client) -> Client:
        pass

    @abstractmethod
    def update(self, client_id: int, data: dict) -> Optional[Client]:
        pass


class AgentRepositoryPort(ABC):
    """Interface for Agent repository operations."""

    @abstractmethod
    def get_by_client_id(self, client_id: int) -> List[Agent]:
        pass


class PaymentRepositoryPort(ABC):
    """Interface for Payment repository operations."""

    @abstractmethod
    def get_by_client_id(self, client_id: int) -> List[Payment]:
        pass

    @abstractmethod
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    def create(self, data: dict) -> Payment:
        pass

    @abstractmethod
    def delete(self, payment_id: int) -> bool:
        pass
