"""
FastAPI application factory.

Creates and configures the HTTP API layer.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from backend.app.api.dependencies.application import (
    set_application,
)
from backend.app.api.router import api_router
from backend.core.kernel.application import Application


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Manage application lifecycle.
    """

    kernel_application = Application()

    set_application(
        kernel_application,
    )

    await kernel_application.start()

    yield

    await kernel_application.stop()


def create_application() -> FastAPI:
    """
    Create FastAPI application.
    """

    application = FastAPI(
        title="Autonomy Engine",
        description=(
            "Autonomous multi-agent automation framework API."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    application.include_router(
        api_router,
    )

    return application


app = create_application()