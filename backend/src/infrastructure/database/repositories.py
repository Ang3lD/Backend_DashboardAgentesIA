from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import List, Optional

from src.domain.models import Client as ClientDomain
from src.domain.models import Agent as AgentDomain
from src.application.ports import ClientRepositoryPort, AgentRepositoryPort
from src.infrastructure.database.config import Base

# ═══════════════════════════════════════════════
#  SQLAlchemy ORM Models
# ═══════════════════════════════════════════════

class ClientModel(Base):
    __tablename__ = "clients"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    slug        = Column(String(50), nullable=False, unique=True)
    plan_id     = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    status      = Column(String(20), default="active")
    start_date  = Column(Date)
    notes       = Column(Text)
    created_at  = Column(DateTime, default=func.now())
    updated_at  = Column(DateTime, default=func.now(), onupdate=func.now())

    agents = relationship("AgentModel", back_populates="client", cascade="all, delete-orphan")
    plan   = relationship("PlanModel", back_populates="clients")


class PlanModel(Base):
    __tablename__ = "plans"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), nullable=False, unique=True)
    price_mxn   = Column(Float, default=0)
    description = Column(Text)
    created_at  = Column(DateTime, default=func.now())

    clients = relationship("ClientModel", back_populates="plan")


class AgentModel(Base):
    __tablename__ = "agents"

    id              = Column(Integer, primary_key=True, index=True)
    client_id       = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    name            = Column(String(100), nullable=False)
    type            = Column(String(50))           # "chatbot" | "agent" | etc.
    description     = Column(Text)
    workflow_id     = Column(String(100))
    chatwoot_inbox  = Column(String(100))
    model           = Column(String(50), default="gpt-4o-mini")
    status          = Column(String(20), default="stopped")
    # Extended fields used by the frontend form (commented out as they are not in DB)
    # system_prompt   = Column(Text, default="You are a helpful AI assistant.")
    # temperature     = Column(Float, default=0.7)
    # max_tokens      = Column(Integer, default=2048)
    # tags            = Column(JSON, default=list)
    # Simulated metrics columns (for demo without real LLM calls)
    # tokens_used     = Column(Integer, default=0)
    # cost_usd        = Column(Float, default=0.0)
    # avg_latency_ms  = Column(Float, default=0.0)
    # error_rate_pct  = Column(Float, default=0.0)
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("ClientModel", back_populates="agents")


# ═══════════════════════════════════════════════
#  Helper: convert ORM → Domain
# ═══════════════════════════════════════════════

def _client_to_domain(c: ClientModel) -> ClientDomain:
    return ClientDomain(
        id=c.id, name=c.name, slug=c.slug, plan_id=c.plan_id, status=c.status,
        start_date=c.start_date, notes=c.notes,
        created_at=c.created_at, updated_at=c.updated_at
    )

def _agent_to_domain(a: AgentModel) -> AgentDomain:
    return AgentDomain(
        id=a.id, client_id=a.client_id, name=a.name, type=a.type,
        description=a.description, workflow_id=a.workflow_id,
        chatwoot_inbox=a.chatwoot_inbox, model=a.model, status=a.status,
        created_at=a.created_at, updated_at=a.updated_at
    )


# ═══════════════════════════════════════════════
#  Repository Implementations
# ═══════════════════════════════════════════════

class ClientRepositorySQL(ClientRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[ClientDomain]:
        return [_client_to_domain(c) for c in self.db.query(ClientModel).all()]

    def get_by_id(self, client_id: int) -> Optional[ClientDomain]:
        c = self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
        return _client_to_domain(c) if c else None

    def save(self, client: ClientDomain) -> ClientDomain:
        db_c = ClientModel(
            name=client.name, slug=client.slug, plan_id=client.plan_id,
            status=client.status, start_date=client.start_date, notes=client.notes
        )
        self.db.add(db_c)
        self.db.commit()
        self.db.refresh(db_c)
        client.id = db_c.id
        client.created_at = db_c.created_at
        client.updated_at = db_c.updated_at
        return client


class AgentRepositorySQL(AgentRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def get_by_client_id(self, client_id: int) -> List[AgentDomain]:
        agents = self.db.query(AgentModel).filter(AgentModel.client_id == client_id).all()
        return [_agent_to_domain(a) for a in agents]

    # ── Extra methods used directly by routes ──

    def get_all(self) -> List[AgentModel]:
        return self.db.query(AgentModel).order_by(AgentModel.created_at.desc()).all()

    def get_by_id(self, agent_id: int) -> Optional[AgentModel]:
        return self.db.query(AgentModel).filter(AgentModel.id == agent_id).first()

    def create(self, data: dict) -> AgentModel:
        agent = AgentModel(**data)
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def update(self, agent_id: int, data: dict) -> Optional[AgentModel]:
        agent = self.get_by_id(agent_id)
        if not agent:
            return None
        for k, v in data.items():
            setattr(agent, k, v)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete(self, agent_id: int) -> bool:
        agent = self.get_by_id(agent_id)
        if not agent:
            return False
        self.db.delete(agent)
        self.db.commit()
        return True

    def delete_all(self) -> None:
        self.db.query(AgentModel).delete()
        self.db.commit()
