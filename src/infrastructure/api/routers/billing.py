from fastapi import APIRouter

router = APIRouter(prefix="/api/billing", tags=["Billing"])

@router.get("")
def get_billing_info():
    """Retrieves detailed billing information (Mock)."""
    return {
        "status": "active",
        "plan": "Enterprise",
        "next_billing_date": "2026-07-01T00:00:00Z",
        "amount_due": 0.00,
        "currency": "USD",
        "features_included": [
            "Unlimited Agents",
            "Priority Support",
            "Advanced Analytics"
        ]
    }
