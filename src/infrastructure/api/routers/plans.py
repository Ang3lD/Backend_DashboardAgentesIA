"""
Router: /api/plans

Endpoints
---------
GET    /api/plans                          — list all plans
"""
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from src.infrastructure.database.config import get_db
from src.infrastructure.database.repositories import PlanModel
from src.infrastructure.api import schemas

router = APIRouter(prefix="/api/plans", tags=["Plans"])

@router.get("", response_model=List[schemas.PlanResponse])
def get_plans(db: Session = Depends(get_db)):
    """Returns the list of all available plans."""
    plans = db.query(PlanModel).all()
    return plans
