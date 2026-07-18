from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from src.infrastructure.database.config import get_db
from src.infrastructure.api import schemas
from src.application.usage_service import UsageService
from src.infrastructure.api.dependencies import get_usage_service

router = APIRouter(prefix="/api/usage", tags=["Usage Logs"])

@router.post("", response_model=schemas.UsageLogResponse)
def log_agent_usage(usage_data: schemas.UsageLogCreate, service: UsageService = Depends(get_usage_service)):
    """Logs the execution of an agent and calculates cost."""
    log = service.log_usage(usage_data.agent_id, usage_data.tokens_in, usage_data.tokens_out)
    if not log:
        raise HTTPException(status_code=404, detail="Agent not found")
    return log

@router.get("/summary", response_model=List[schemas.UsageSummaryItem])
def get_usage_summary(period: str = None, service: UsageService = Depends(get_usage_service)):
    """Returns the total usage summary for all clients for a given period (YYYY-MM). Defaults to current month."""
    import re
    if period and not re.match(r"^\d{4}-\d{2}$", period):
        raise HTTPException(status_code=400, detail="El parámetro 'period' debe tener el formato YYYY-MM (ej. 2026-06)")
        
    if not period:
        period = datetime.now().strftime("%Y-%m")
    
    return service.get_summary(period)
