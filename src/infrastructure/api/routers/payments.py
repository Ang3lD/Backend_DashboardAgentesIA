"""
Router: Payments (nested under /api/clients/{id})

Endpoints
---------
GET    /api/clients/{id}/payments               — payment history
POST   /api/clients/{id}/payments               — register payment
DELETE /api/clients/{id}/payments/{payment_id}  — delete payment
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from typing import List
import csv
import io
from datetime import datetime

from src.infrastructure.api import schemas
from src.application.services import BillingService
from src.infrastructure.api.dependencies import get_billing_service

router = APIRouter(prefix="/api/clients", tags=["Payments"])


@router.get("/{id}/payments", response_model=List[schemas.PaymentResponse])
def get_payments(
    id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Returns the payment history for a client, ordered by period (newest first)."""
    summary = service.get_billing_summary(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Client not found")
    return service.get_payments(id)


@router.get("/{id}/payments/export")
def export_payments(
    id: int,
    service: BillingService = Depends(get_billing_service),
):
    """Exports payment history for a client to a CSV file."""
    client = service.client_repository.get_by_id(id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    payments = service.get_payments(id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["periodo", "monto_mxn", "fecha_pago", "notas"])
    
    for p in payments:
        writer.writerow([
            p.period_month,
            p.amount_mxn,
            p.paid_at.isoformat() if p.paid_at else "",
            p.notes or ""
        ])

    current_month = datetime.now().strftime("%Y-%m")
    filename = f"pagos_{client.slug}_{current_month}.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )



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
