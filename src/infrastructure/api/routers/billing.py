"""
Router: Billing & Payments (nested under /api/clients/{id})

Endpoints
---------
GET    /api/clients/{id}/billing                   — BillingSummary
GET    /api/clients/{id}/payments                  — payment history
POST   /api/clients/{id}/payments                  — register payment
DELETE /api/clients/{id}/payments/{payment_id}     — delete payment
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.infrastructure.api import schemas
from src.application.services import BillingService
from src.infrastructure.api.dependencies import get_billing_service

router = APIRouter(prefix="/api/clients", tags=["Billing & Payments"])


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


@router.get("/{id}/payments", response_model=List[schemas.PaymentResponse])
def get_payments(
    id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Returns the payment history for a client, ordered by period (newest first)."""
    # Verify client exists via billing summary check
    summary = service.get_billing_summary(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Client not found")
    return service.get_payments(id)


@router.post("/{id}/payments", response_model=schemas.PaymentResponse, status_code=201)
def create_payment(
    id: int,
    payment_data: schemas.PaymentCreate,
    service: BillingService = Depends(get_billing_service),
):
    """Registers a new payment for a client."""
    summary = service.get_billing_summary(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Client not found")
    data = payment_data.model_dump()
    return service.create_payment(id, data)


@router.delete("/{id}/payments/{payment_id}", status_code=204)
def delete_payment(
    id: int,
    payment_id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Deletes a specific payment. Returns 404 if payment doesn't exist or doesn't belong to this client."""
    deleted = service.delete_payment(id, payment_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Payment not found or does not belong to this client",
        )
