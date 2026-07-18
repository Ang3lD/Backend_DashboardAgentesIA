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

@dataclass
class Payment:
    """Entity representing a monthly payment registered for a Client."""
    client_id: int
    period_month: str          # "YYYY-MM"
    amount_mxn: float
    paid_at: date
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class UsageLog:
    """Entity representing a single agent execution log."""
    agent_id: int
    client_id: int
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: datetime
    id: Optional[int] = None
