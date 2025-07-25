from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.database.session import get_session

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.2.0"
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Readiness check that includes database connectivity."""
    response = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.2.0",
        "database": "unknown"
    }
    
    try:
        # Simple database connectivity check
        result = session.exec(select(1))
        _ = result.first()
        response["database"] = "connected"
    except Exception as e:
        response["status"] = "unhealthy"
        response["database"] = f"error: {str(e)}"
        
    return response