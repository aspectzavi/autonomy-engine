"""
Health API routes.

Provides liveness and readiness checks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.api.dependencies.application import (
    get_application,
)
from backend.core.kernel.application import Application


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def health(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return application health.
    """

    return {
        "status": "healthy",
        "running": app.is_running,
        "runtime": app.runtime.state.value,
    }


@router.get("/ready")
async def readiness(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Readiness probe.
    """

    return {
        "ready": app.is_running,
    }