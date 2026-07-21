"""
API router aggregation.

Combines all application API routes.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.runtime import router as runtime_router
from backend.app.api.routes.services import (router as services_router,)
from backend.app.api.routes.agents import (
    router as agents_router,
)


api_router = APIRouter()

api_router.include_router(
    health_router,
)

api_router.include_router(
    runtime_router,
)

api_router.include_router(
    services_router,
)

api_router.include_router(
    agents_router,
)