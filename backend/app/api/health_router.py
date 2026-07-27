from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version
from typing import Any, Dict

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.models import AccessToken
from app.database.session import get_session

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

try:
    APP_VERSION = get_version("automation_server_backend")
except PackageNotFoundError:
    APP_VERSION = "unknown"


async def _auth_mode(session: AsyncSession) -> str:
    """Report whether API authentication is enforced.

    "open" means the access token table is empty, so requests are served
    without authentication (install/development bootstrap mode).
    """
    try:
        result = await session.execute(
            select(AccessToken).where(AccessToken.deleted == False).limit(1)  # noqa: E712
        )
        return "enforced" if result.first() is not None else "open"
    except Exception:
        return "unknown"


@router.get("", response_model=Dict[str, Any])
async def health_check(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": APP_VERSION,
        "auth": await _auth_mode(session),
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Readiness check that includes database connectivity.

    Returns 503 when the database is unreachable so healthchecks and
    orchestrators can act on the HTTP status alone.
    """
    body = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": APP_VERSION,
        "database": "unknown",
    }

    try:
        # Simple database connectivity check
        result = await session.execute(select(1))
        _ = result.first()
        body["database"] = "connected"
    except Exception as e:
        body["status"] = "unhealthy"
        body["database"] = f"error: {str(e)}"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return body
