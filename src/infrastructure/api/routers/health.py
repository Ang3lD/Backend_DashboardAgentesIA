from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.infrastructure.database.config import get_db

router = APIRouter(prefix="/api/health", tags=["System Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Verifies the health of the API and database connectivity."""
    health_status = {
        "status": "ok",
        "database": "disconnected"
    }
    try:
        # Execute a simple query to verify database connection
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "error"
        health_status["details"] = str(e)
        raise HTTPException(status_code=503, detail=health_status)
        
    return health_status
