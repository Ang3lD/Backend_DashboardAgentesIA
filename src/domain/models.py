from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

# Domain layer: Core business entities
# Independent of databases or web frameworks

@dataclass
class Client:
    """Entity representing a Client in the system."""
    name: str
    slug: str
    plan_id: Optional[int]
    status: str
    start_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class Agent:
    """Entity representing an Agent assigned to a Client."""
    name: str
    client_id: int
    type: Optional[str] = None
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    chatwoot_inbox: Optional[str] = None
    model: str = "gpt-4o-mini"
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
