"""
Router: Billing (nested under /api/clients/{id})

Endpoints
---------
GET    /api/clients/{id}/billing   — BillingSummary
"""
from fastapi import APIRouter, Depends, HTTPException

from src.infrastructure.api import schemas
from src.application.services import BillingService
from src.infrastructure.api.dependencies import get_billing_service

router = APIRouter(prefix="/api/clients", tags=["Billing"])


@router.get("/{id}/billing", response_model=schemas.BillingSummaryResponse)
def get_billing_summary(
    id: int,
    service: BillingService = Depends(get_billing_service),
):
    """
    Returns the full billing summary for a client:
    months active, months paid, amount owed, billing status,
    paid/missing periods, and full payment history.
    """
    summary = service.get_billing_summary(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Client not found")
    return summary
