"""
Runtime API routes.

Provides external runtime control
and diagnostics.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.api.dependencies.application import (
    get_application,
)
from backend.core.kernel.application import Application


router = APIRouter(
    prefix="/runtime",
    tags=["runtime"],
)


@router.get("")
async def runtime_status(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return runtime status.
    """

    return {
        "running": app.is_running,
        "state": app.runtime.state.value,
    }


@router.get("/diagnostics")
async def diagnostics(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return runtime diagnostics.
    """

    return app.diagnostics()


@router.post("/restart")
async def restart(
    app: Application = Depends(get_application),
) -> dict[str, str]:
    """
    Restart runtime.
    """

    await app.restart()

    return {
        "status": "restarted",
    }


@router.post("/stop")
async def stop(
    app: Application = Depends(get_application),
) -> dict[str, str]:
    """
    Stop runtime.
    """

    await app.stop()

    return {
        "status": "stopped",
    }