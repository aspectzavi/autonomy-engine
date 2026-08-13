"""
Runtime dependency shutdown order tests.
"""

from __future__ import annotations

from typing import ClassVar

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import ServiceRegistration
from backend.core.kernel.service import KernelService


class ShutdownOrderedService(KernelService):
    """
    Service that records shutdown order.
    """

    shutdown_events: ClassVar[list[str]] = []

    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name=name,
                version="1.0.0",
            ),
        )

    async def on_start(
        self,
    ) -> None:
        #
        # Startup isn't important for this test.
        #
        return

    async def on_stop(
        self,
    ) -> None:
        self.shutdown_events.append(
            self.metadata.name,
        )


@pytest.mark.asyncio
async def test_runtime_dependency_shutdown_order() -> None:
    """
    Runtime should stop services in reverse dependency order.
    """

    ShutdownOrderedService.shutdown_events.clear()

    bootstrap = KernelBootstrap()

    database = ShutdownOrderedService("database")
    cache = ShutdownOrderedService("cache")
    api = ShutdownOrderedService("api")

    bootstrap.register(
        ServiceRegistration(
            metadata=database.metadata,
            service=database,
        )
    )

    bootstrap.register(
        ServiceRegistration(
            metadata=cache.metadata,
            service=cache,
        )
    )

    bootstrap.register(
        ServiceRegistration(
            metadata=api.metadata,
            service=api,
        )
    )

    #
    # api -> cache -> database
    #
    bootstrap.depends_on(
        "cache",
        "database",
    )

    bootstrap.depends_on(
        "api",
        "cache",
    )

    runtime = bootstrap.build()

    await runtime.start()
    await runtime.stop()

    events = ShutdownOrderedService.shutdown_events

    #
    # Verify reverse dependency ordering.
    #
    assert events.index("api") < events.index("cache")
    assert events.index("cache") < events.index("database")

    diagnostics = runtime.diagnostics()

    assert diagnostics["state"] == "stopped"
    assert diagnostics["is_running"] is False