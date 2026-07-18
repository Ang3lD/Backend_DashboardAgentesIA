from typing import List, Optional
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta

from src.domain.models import Client, Agent, Payment
from src.application.ports import ClientRepositoryPort, AgentRepositoryPort, PaymentRepositoryPort


# ─────────────────────────────────────────────────────────────────────────────
#  ClientService
# ─────────────────────────────────────────────────────────────────────────────

class ClientService:
    def __init__(
        self,
        client_repository: ClientRepositoryPort,
        agent_repository: AgentRepositoryPort,
    ):
        self.client_repository = client_repository
        self.agent_repository = agent_repository

    def get_clients(self, status: Optional[str] = None) -> List[Client]:
        """Retrieves clients, optionally filtered by status."""
        return self.client_repository.get_all(status=status)

    def get_client(self, client_id: int) -> Optional[Client]:
        """Retrieves a specific client by ID."""
        return self.client_repository.get_by_id(client_id)

    def create_client(self, client_data: Client) -> Client:
        """Creates and saves a new client."""
        return self.client_repository.save(client_data)

    def update_client(self, client_id: int, data: dict) -> Optional[Client]:
        """Updates an existing client with the provided fields."""
        return self.client_repository.update(client_id, data)

    # ── Agents ────────────────────────────────────────────────────────────────

    def get_client_agents(self, client_id: int) -> List[Agent]:
        """Retrieves all agents assigned to a specific client."""
        return self.agent_repository.get_by_client_id(client_id)

    def create_agent(self, client_id: int, data: dict) -> object:
        """Creates a new agent under a client."""
        data["client_id"] = client_id
        return self.agent_repository.create(data)

    def update_agent(self, client_id: int, agent_id: int, data: dict) -> Optional[object]:
        """Updates an agent that belongs to a specific client."""
        agent = self.agent_repository.get_by_id(agent_id)
        if not agent or agent.client_id != client_id:
            return None
        return self.agent_repository.update(agent_id, data)


# ─────────────────────────────────────────────────────────────────────────────
#  BillingService
# ─────────────────────────────────────────────────────────────────────────────

class BillingService:
    def __init__(
        self,
        client_repository: ClientRepositoryPort,
        payment_repository: PaymentRepositoryPort,
    ):
        self.client_repository = client_repository
        self.payment_repository = payment_repository

    # ── Internal helper ───────────────────────────────────────────────────────

    def _build_summary(self, client_id: int) -> Optional[dict]:
        """
        Builds the BillingSummary dict for a client.
        Returns None if the client doesn't exist.
        """
        # Use get_orm_by_id so we can access plan relationship
        client_orm = self.client_repository.get_orm_by_id(client_id)
        if not client_orm:
            return None

        plan = client_orm.plan
        monthly_fee = float(plan.price_mxn) if plan else 0.0
        plan_name = plan.name if plan else None

        today = date.today()
        start = client_orm.start_date  # date or None

        # Calculate months active
        if start:
            delta = relativedelta(today, start)
            months_active = delta.years * 12 + delta.months
            # Include partial current month
            if today.day >= 1:
                months_active += 1
        else:
            months_active = 0

        # Payments
        payments = self.payment_repository.get_by_client_id(client_id)
        paid_periods = sorted({p.period_month for p in payments})
        months_paid = len(paid_periods)
        months_owed = max(0, months_active - months_paid)
        total_owed_mxn = months_owed * monthly_fee

        # Billing status
        if months_owed == 0:
            billing_status = "current"
        elif months_owed <= 2:
            billing_status = "overdue"
        else:
            billing_status = "critical"

        # Last payment
        last_paid_at = None
        days_since_payment = None
        if payments:
            last_paid_at = max(p.paid_at for p in payments)
            days_since_payment = (today - last_paid_at).days

        # Missing periods: every month from start_date to today not in paid_periods
        missing_periods: List[str] = []
        if start and months_active > 0:
            cursor = date(start.year, start.month, 1)
            end_cursor = date(today.year, today.month, 1)
            while cursor <= end_cursor:
                label = cursor.strftime("%Y-%m")
                if label not in paid_periods:
                    missing_periods.append(label)
                cursor += relativedelta(months=1)

        # Payment Alerts
        next_payment_due = missing_periods[0] if missing_periods else today.strftime("%Y-%m")
        
        days_until_overdue = None
        if billing_status == "current":
            import calendar
            last_day_of_month = calendar.monthrange(today.year, today.month)[1]
            days_until_overdue = last_day_of_month - today.day
            
        overdue_since = None
        if months_owed > 0 and missing_periods:
            y, m = missing_periods[0].split("-")
            overdue_since = date(int(y), int(m), 1).isoformat()

        # Serialize payments
        payments_data = [
            {
                "id": p.id,
                "client_id": p.client_id,
                "period_month": p.period_month,
                "amount_mxn": p.amount_mxn,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
                "notes": p.notes,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in payments
        ]

        return {
            "client_id": client_orm.id,
            "client_name": client_orm.name,
            "plan_name": plan_name,
            "monthly_fee": monthly_fee,
            "start_date": client_orm.start_date.isoformat() if client_orm.start_date else None,
            "months_active": months_active,
            "months_paid": months_paid,
            "months_owed": months_owed,
            "total_owed_mxn": total_owed_mxn,
            "last_paid_at": last_paid_at.isoformat() if last_paid_at else None,
            "days_since_payment": days_since_payment,
            "billing_status": billing_status,
            "next_payment_due": next_payment_due,
            "days_until_overdue": days_until_overdue,
            "overdue_since": overdue_since,
            "paid_periods": paid_periods,
            "missing_periods": missing_periods,
            "payments": payments_data,
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def get_billing_summary(self, client_id: int) -> Optional[dict]:
        return self._build_summary(client_id)

    def get_payments(self, client_id: int) -> List[Payment]:
        return self.payment_repository.get_by_client_id(client_id)

    def create_payment(self, client_id: int, data: dict) -> Payment:
        data["client_id"] = client_id
        return self.payment_repository.create(data)

    def delete_payment(self, client_id: int, payment_id: int) -> bool:
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment or payment.client_id != client_id:
            return False
        return self.payment_repository.delete(payment_id)
