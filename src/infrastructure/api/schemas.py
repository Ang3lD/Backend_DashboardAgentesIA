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

class ClientUpdate(BaseModel):
    """Schema for partial update of a client (PUT)."""
    name: Optional[str] = None
    slug: Optional[str] = None
    plan_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None

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
    status: str = "active"

class AgentCreate(BaseModel):
    """Schema for creating an agent under a client."""
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    chatwoot_inbox: Optional[str] = None
    model: str = "gpt-4o-mini"
    status: str = "active"

class AgentUpdate(BaseModel):
    """Schema for partial agent update (PUT)."""
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    chatwoot_inbox: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None

class AgentResponse(BaseModel):
    """Schema for returning agent data."""
    id: int
    client_id: Optional[int] = None
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    chatwoot_inbox: Optional[str] = None
    model: str = "gpt-4o-mini"
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Payment schemas ──────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    """Schema for registering a payment."""
    period_month: str          # "YYYY-MM"
    amount_mxn: float
    paid_at: date
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    """Schema for returning payment data."""
    id: int
    client_id: int
    period_month: str
    amount_mxn: float
    paid_at: date
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Billing Summary schema ───────────────────────────────────────────────────

class BillingSummaryResponse(BaseModel):
    """Full billing summary for a client."""
    client_id: int
    client_name: str
    plan_name: Optional[str] = None
    monthly_fee: float
    start_date: Optional[str] = None
    months_active: int
    months_paid: int
    months_owed: int
    total_owed_mxn: float
    last_paid_at: Optional[str] = None
    days_since_payment: Optional[int] = None
    billing_status: str          # "current" | "overdue" | "critical"
    next_payment_due: str
    days_until_overdue: Optional[int] = None
    overdue_since: Optional[str] = None
    paid_periods: List[str]
    missing_periods: List[str]
    payments: List[dict]


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

# ─── Plan schemas ─────────────────────────────────────────────────────────────

class PlanResponse(BaseModel):
    id: int
    name: str
    price_mxn: float
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ─── Usage schemas ────────────────────────────────────────────────────────────

class UsageLogCreate(BaseModel):
    agent_id: int
    tokens_in: int
    tokens_out: int

class UsageBreakdownItem(BaseModel):
    agent_id: int
    model: str
    tokens_in: int
    tokens_out: int
    total_tokens: int
    cost_usd: float
    runs: int

class ClientUsageResponse(BaseModel):
    client_id: int
    client_name: str
    period: str
    total_tokens: int
    total_cost_usd: float
    total_runs: int
    breakdown: List[UsageBreakdownItem]

class UsageSummaryItem(BaseModel):
    client_id: int
    client_name: str
    total_tokens: int
    total_cost_usd: float
    total_runs: int

class UsageLogResponse(BaseModel):
    id: int
    agent_id: int
    client_id: int
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: datetime

    class Config:
        from_attributes = True
