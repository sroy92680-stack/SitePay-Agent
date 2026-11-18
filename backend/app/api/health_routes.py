#Owner::ANIKET::ANHOTRA = MR.Panda
"""Liveness and database readiness endpoints for health probes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.database import get_database_session

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def liveness() -> dict[str, str]:
    """Confirm the web process can execute a request without touching secrets."""
    return {"status": "alive"}


@router.get("/ready")
def readiness(session: Session = Depends(get_database_session)) -> dict[str, str]:
    """Check database connectivity, without exposing connection details."""
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unavailable") from error
    return {"status": "ready"}
