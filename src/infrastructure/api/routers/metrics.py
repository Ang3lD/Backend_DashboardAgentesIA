from fastapi import APIRouter, Depends
from typing import List

from src.infrastructure.api import schemas
from src.application.metrics_service import MetricsService
from src.infrastructure.api.dependencies import get_metrics_service

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])

@router.get("/mrr", response_model=List[schemas.MrrHistoryItem])
def get_mrr_history(
    months: int = 6,
    service: MetricsService = Depends(get_metrics_service),
):
    """Returns historical MRR data month by month."""
    return service.get_mrr_history(months)

@router.get("/summary", response_model=schemas.GlobalMetricsSummary)
def get_global_summary(
    service: MetricsService = Depends(get_metrics_service),
):
    """Returns global platform KPIs."""
    return service.get_global_summary()
