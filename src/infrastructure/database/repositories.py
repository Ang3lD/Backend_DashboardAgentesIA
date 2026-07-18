from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, Float, Numeric
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from typing import List, Optional

from src.domain.models import Client as ClientDomain
from src.domain.models import Agent as AgentDomain
from src.domain.models import Payment as PaymentDomain
from src.domain.models import UsageLog as UsageLogDomain
from src.application.ports import ClientRepositoryPort, AgentRepositoryPort, PaymentRepositoryPort, UsageLogRepositoryPort
from src.infrastructure.database.config import Base

# ═══════════════════════════════════════════════
#  SQLAlchemy ORM Models
# ═══════════════════════════════════════════════

class PlanModel(Base):
    __tablename__ = "plans"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), nullable=False, unique=True)
    price_mxn   = Column(Numeric(10, 2), default=0)
    description = Column(Text)
    created_at  = Column(DateTime, default=func.now())

    clients = relationship("ClientModel", back_populates="plan")


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

    agents   = relationship("AgentModel", back_populates="client", cascade="all, delete-orphan")
    plan     = relationship("PlanModel", back_populates="clients")
    payments = relationship("PaymentModel", back_populates="client", cascade="all, delete-orphan")


class AgentModel(Base):
    __tablename__ = "agents"

    id              = Column(Integer, primary_key=True, index=True)
    client_id       = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name            = Column(String(100), nullable=False)
    type            = Column(String(50))
    description     = Column(Text)
    workflow_id     = Column(String(100))
    chatwoot_inbox  = Column(String(100))
    model           = Column(String(50), default="gpt-4o-mini")
    status          = Column(String(20), default="active")
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("ClientModel", back_populates="agents")
    usage_logs = relationship("UsageLogModel", back_populates="agent", cascade="all, delete-orphan")


class PaymentModel(Base):
    __tablename__ = "payments"

    id           = Column(Integer, primary_key=True, index=True)
    client_id    = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    period_month = Column(String(7), nullable=False)   # "YYYY-MM"
    amount_mxn   = Column(Numeric(10, 2), nullable=False)
    paid_at      = Column(Date, nullable=False)
    notes        = Column(Text)
    created_at   = Column(DateTime, default=func.now())

    client = relationship("ClientModel", back_populates="payments")

class UsageLogModel(Base):
    __tablename__ = "usage_logs"

    id         = Column(Integer, primary_key=True, index=True)
    agent_id   = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id  = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    model      = Column(String(50), nullable=False)
    tokens_in  = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost_usd   = Column(Numeric(10, 4), default=0)
    timestamp  = Column(DateTime, default=func.now())

    agent = relationship("AgentModel", back_populates="usage_logs")
    client = relationship("ClientModel")


# ═══════════════════════════════════════════════
#  Helpers: convert ORM → Domain
# ═══════════════════════════════════════════════

def _client_to_domain(c: ClientModel) -> ClientDomain:
    return ClientDomain(
        id=c.id, name=c.name, slug=c.slug, plan_id=c.plan_id, status=c.status,
        start_date=c.start_date, notes=c.notes,
        created_at=c.created_at, updated_at=c.updated_at,
    )

def _agent_to_domain(a: AgentModel) -> AgentDomain:
    return AgentDomain(
        id=a.id, client_id=a.client_id, name=a.name, type=a.type,
        description=a.description, workflow_id=a.workflow_id,
        chatwoot_inbox=a.chatwoot_inbox, model=a.model, status=a.status,
        created_at=a.created_at, updated_at=a.updated_at,
    )

def _payment_to_domain(p: PaymentModel) -> PaymentDomain:
    return PaymentDomain(
        id=p.id, client_id=p.client_id, period_month=p.period_month,
        amount_mxn=float(p.amount_mxn), paid_at=p.paid_at,
        notes=p.notes, created_at=p.created_at,
    )

def _usage_log_to_domain(u: UsageLogModel) -> UsageLogDomain:
    return UsageLogDomain(
        id=u.id, agent_id=u.agent_id, client_id=u.client_id, model=u.model,
        tokens_in=u.tokens_in, tokens_out=u.tokens_out, cost_usd=float(u.cost_usd),
        timestamp=u.timestamp,
    )


# ═══════════════════════════════════════════════
#  Repository Implementations
# ═══════════════════════════════════════════════

class ClientRepositorySQL(ClientRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, status: Optional[str] = None) -> List[ClientDomain]:
        q = self.db.query(ClientModel)
        if status:
            q = q.filter(ClientModel.status == status)
        return [_client_to_domain(c) for c in q.all()]

    def get_by_id(self, client_id: int) -> Optional[ClientDomain]:
        c = self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
        return _client_to_domain(c) if c else None

    def save(self, client: ClientDomain) -> ClientDomain:
        db_c = ClientModel(
            name=client.name, slug=client.slug, plan_id=client.plan_id,
            status=client.status, start_date=client.start_date, notes=client.notes,
        )
        self.db.add(db_c)
        self.db.commit()
        self.db.refresh(db_c)
        client.id = db_c.id
        client.created_at = db_c.created_at
        client.updated_at = db_c.updated_at
        return client

    def delete(self, client_id: int) -> bool:
        db_c = self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
        if not db_c:
            return False
        self.db.delete(db_c)
        self.db.commit()
        return True

    def update(self, client_id: int, data: dict) -> Optional[ClientDomain]:
        db_c = self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
        if not db_c:
            return None
        for k, v in data.items():
            if v is not None:
                setattr(db_c, k, v)
        self.db.commit()
        self.db.refresh(db_c)
        return _client_to_domain(db_c)

    # ── Raw ORM accessors used by billing service ──────────────────────────────

    def get_orm_by_id(self, client_id: int) -> Optional[ClientModel]:
        return self.db.query(ClientModel).filter(ClientModel.id == client_id).first()


class AgentRepositorySQL(AgentRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def get_by_client_id(self, client_id: int) -> List[AgentDomain]:
        agents = self.db.query(AgentModel).filter(AgentModel.client_id == client_id).all()
        return [_agent_to_domain(a) for a in agents]

    def delete(self, agent_id: int) -> bool:
        db_a = self.db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not db_a:
            return False
        self.db.delete(db_a)
        self.db.commit()
        return True

    # ── Extra methods used directly by routes ──────────────────────────────────

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
            if v is not None:
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


class PaymentRepositorySQL(PaymentRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def get_by_client_id(self, client_id: int) -> List[PaymentDomain]:
        rows = (
            self.db.query(PaymentModel)
            .filter(PaymentModel.client_id == client_id)
            .order_by(PaymentModel.period_month.desc())
            .all()
        )
        return [_payment_to_domain(p) for p in rows]

    def get_by_id(self, payment_id: int) -> Optional[PaymentDomain]:
        p = self.db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
        return _payment_to_domain(p) if p else None

    def create(self, data: dict) -> PaymentDomain:
        p = PaymentModel(**data)
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return _payment_to_domain(p)

    def delete(self, payment_id: int) -> bool:
        p = self.db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
        if not p:
            return False
        self.db.delete(p)
        self.db.commit()
        return True

class UsageLogRepositorySQL(UsageLogRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> UsageLogDomain:
        ul = UsageLogModel(**data)
        self.db.add(ul)
        self.db.commit()
        self.db.refresh(ul)
        return _usage_log_to_domain(ul)

    def _get_period_bounds(self, period: str):
        from datetime import date
        from dateutil.relativedelta import relativedelta
        year, month = map(int, period.split("-"))
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1)
        return start_date, end_date

    def get_by_client_id_and_period(self, client_id: int, period: str) -> List[UsageLogDomain]:
        start_date, end_date = self._get_period_bounds(period)
        rows = (
            self.db.query(UsageLogModel)
            .filter(UsageLogModel.client_id == client_id)
            .filter(UsageLogModel.timestamp >= start_date)
            .filter(UsageLogModel.timestamp < end_date)
            .order_by(UsageLogModel.timestamp.desc())
            .all()
        )
        return [_usage_log_to_domain(u) for u in rows]

    def get_summary_by_period(self, period: str) -> List[dict]:
        from sqlalchemy import func
        start_date, end_date = self._get_period_bounds(period)
        
        results = (
            self.db.query(
                UsageLogModel.client_id,
                func.sum(UsageLogModel.tokens_in + UsageLogModel.tokens_out).label("total_tokens"),
                func.sum(UsageLogModel.cost_usd).label("total_cost_usd"),
                func.count(UsageLogModel.id).label("total_runs")
            )
            .filter(UsageLogModel.timestamp >= start_date)
            .filter(UsageLogModel.timestamp < end_date)
            .group_by(UsageLogModel.client_id)
            .all()
        )
        
        return [
            {
                "client_id": r.client_id,
                "total_tokens": int(r.total_tokens) if r.total_tokens else 0,
                "total_cost_usd": float(r.total_cost_usd) if r.total_cost_usd else 0.0,
                "total_runs": int(r.total_runs) if r.total_runs else 0
            }
            for r in results
        ]
