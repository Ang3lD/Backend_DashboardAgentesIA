from sqlalchemy.orm import Session
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List

from src.infrastructure.database.repositories import ClientModel, PlanModel, PaymentModel, AgentModel
from src.application.services import BillingService

class MetricsService:
    def __init__(self, db: Session, billing_service: BillingService):
        self.db = db
        self.billing_service = billing_service

    def get_mrr_history(self, months: int = 6) -> List[dict]:
        """
        Returns historical MRR data for the past `months` months.
        Calculates expected MRR from active clients and actual collected from payments.
        """
        history = []
        today = date.today()
        
        # For each month going backwards
        for i in range(months - 1, -1, -1):
            target_date = today - relativedelta(months=i)
            month_str = target_date.strftime("%Y-%m")
            
            # Start of next month to check start_date < start_of_next_month
            next_month_date = target_date + relativedelta(months=1)
            start_of_next_month = date(next_month_date.year, next_month_date.month, 1)
            
            # MRR esperado y Clientes activos
            # Asumimos que un cliente estaba activo si status == "active" 
            # y start_date < start_of_next_month
            active_clients_query = (
                self.db.query(ClientModel)
                .join(PlanModel, ClientModel.plan_id == PlanModel.id)
                .filter(ClientModel.status == "active")
                .filter(ClientModel.start_date < start_of_next_month)
            )
            
            clientes_activos = active_clients_query.count()
            # Sum of plan prices
            mrr_esperado = sum(float(c.plan.price_mxn) for c in active_clients_query.all()) if clientes_activos > 0 else 0.0
            
            # Cobrado real y pagos recibidos
            payments = (
                self.db.query(PaymentModel)
                .filter(PaymentModel.period_month == month_str)
                .all()
            )
            pagos_recibidos = len(payments)
            cobrado_real = sum(float(p.amount_mxn) for p in payments) if pagos_recibidos > 0 else 0.0
            
            history.append({
                "month": month_str,
                "mrr_esperado": mrr_esperado,
                "cobrado_real": cobrado_real,
                "clientes_activos": clientes_activos,
                "pagos_recibidos": pagos_recibidos
            })
            
        return history

    def get_global_summary(self) -> dict:
        """
        Returns global KPIs.
        """
        total_clients = self.db.query(ClientModel).count()
        active_clients = self.db.query(ClientModel).filter(ClientModel.status == "active").count()
        agents_count = self.db.query(AgentModel).count()
        
        active_clients_list = self.db.query(ClientModel).join(PlanModel).filter(ClientModel.status == "active").all()
        mrr_actual = sum(float(c.plan.price_mxn) for c in active_clients_list)
        
        total_owed = 0.0
        clients = self.db.query(ClientModel).all()
        for c in clients:
            summary = self.billing_service.get_billing_summary(c.id)
            if summary:
                total_owed += summary.get("total_owed_mxn", 0.0)
                
        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "mrr_actual": mrr_actual,
            "total_owed": total_owed,
            "agents_count": agents_count
        }
