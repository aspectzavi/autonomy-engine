"""
Runtime dependency order tests.
"""

from __future__ import annotations

from typing import ClassVar

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import ServiceRegistration
from backend.core.kernel.service import KernelService


class OrderedService(KernelService):
    """
    Test service that records lifecycle order.
    """

    lifecycle_events: ClassVar[list[str]] = []

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
        self.lifecycle_events.append(
            f"start:{self.metadata.name}"
        )

    async def on_stop(
        self,
    ) -> None:
        self.lifecycle_events.append(
            f"stop:{self.metadata.name}"
        )


@pytest.mark.asyncio
async def test_runtime_dependency_order() -> None:
    """
    Runtime should honor dependency ordering during
    startup and shutdown.
    """

    OrderedService.lifecycle_events.clear()

    bootstrap = KernelBootstrap()

    database = OrderedService("database")
    cache = OrderedService("cache")
    api = OrderedService("api")

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
    # api depends on cache
    # cache depends on database
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

    #
    # Only verify relative ordering.
    #
    events = OrderedService.lifecycle_events

    start_events = [
        event
        for event in events
        if event.startswith("start:")
    ]

    stop_events = [
        event
        for event in events
        if event.startswith("stop:")
    ]

    #
    # Startup order:
    # database -> cache -> api
    #
    assert (
        start_events.index("start:database")
        < start_events.index("start:cache")
        < start_events.index("start:api")
    )

    #
    # Shutdown order:
    # api -> cache -> database
    #
    assert (
        stop_events.index("stop:api")
        < stop_events.index("stop:cache")
        < stop_events.index("stop:database")
    )

    diagnostics = runtime.diagnostics()

    assert diagnostics["state"] == "stopped"
    assert diagnostics["is_running"] is False