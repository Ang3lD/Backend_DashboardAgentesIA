from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime

# ─── Client schemas ───────────────────────────────────────────────────────────

class ClientBase(BaseModel):
    name: str
    slug: str
    plan_id: Optional[int] = None
    status: str = "active"
    start_date: Optional[date] = None
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    pass

class ClientResponse(ClientBase):
    """Schema for returning client data (includes ID and timestamps)."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Agent schemas ────────────────────────────────────────────────────────────

class AgentBase(BaseModel):
    name: str
    client_id: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    chatwoot_inbox: Optional[str] = None
    model: str = "gpt-4o-mini"
    status: str = "stopped"

class AgentCreate(BaseModel):
    """Schema for creating or updating an agent."""
    name: str
    description: Optional[str] = None
    model: str = "gpt-4o-mini"
    status: str = "stopped"
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    tags: Optional[List[str]] = []
    client_id: Optional[int] = None
    type: Optional[str] = None

class AgentUpdate(BaseModel):
    """Schema for partial agent update (PATCH)."""
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tags: Optional[List[str]] = None
    client_id: Optional[int] = None
    type: Optional[str] = None

class AgentResponse(BaseModel):
    """Schema for returning agent data."""
    id: int
    name: str
    client_id: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    chatwoot_inbox: Optional[str] = None
    model: str = "gpt-4o-mini"
    status: str = "stopped"
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    tags: Optional[List[str]] = []
    agent_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Metrics schemas ──────────────────────────────────────────────────────────

class MetricsOverview(BaseModel):
    total_tokens: int
    total_cost_usd: float
    total_runs: int
    active_agents: int
    paused_agents: int
    error_agents: int
    total_agents: int
    error_rate_pct: float
    avg_latency_ms: float

class TimeseriesPoint(BaseModel):
    date: str
    tokens: int
    cost: float
    runs: int
    avg_latency_ms: float

class ModelMetric(BaseModel):
    model: str
    tokens: int
    cost: float
    runs: int

class AgentMetric(BaseModel):
    agent_id: int
    name: str
    model: str
    status: str
    tokens: int
    cost: float
    avg_latency_ms: float
    error_rate_pct: float

class AgentLogEntry(BaseModel):
    id: int
    timestamp: datetime
    tokens_in: int
    tokens_out: int
    latency_ms: int
    success: bool


# ─── Model list schema ────────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str


# ─── Client dashboard schema ──────────────────────────────────────────────────

class ClientSummary(BaseModel):
    total_tokens: int
    total_cost_usd: float
    active: int
    total_agents: int
    chatbots: int
    agents: int
    error_rate_pct: float
    avg_latency_ms: float

class ClientDashboardAgent(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model: str
    status: str
    agent_type: Optional[str] = None
    tokens: int = 0
    cost: float = 0.0
    avg_latency_ms: float = 0.0
    error_rate_pct: float = 0.0

class ClientDashboardResponse(BaseModel):
    client: Any  # ClientResponse
    summary: ClientSummary
    agents: List[ClientDashboardAgent]
    timeseries: List[TimeseriesPoint]
