"""
Service API routes.

Provides visibility into kernel-managed services.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.api.dependencies.application import (
    get_application,
)
from backend.core.kernel.application import Application


router = APIRouter(
    prefix="/services",
    tags=["services"],
)


@router.get("")
async def services(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return registered services.
    """

    return {
        "services": (
            app.runtime.registry.diagnostics()
        ),
    }


@router.get("/diagnostics")
async def service_diagnostics(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return full runtime diagnostics.
    """

    return {
        "runtime": (
            app.runtime.diagnostics()
        ),
    }