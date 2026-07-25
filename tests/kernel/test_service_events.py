"""
KernelService event publishing tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.observability.events import EventBus


class DummyService(KernelService):
    """
    Service used to verify lifecycle event publication.
    """

    def __init__(
        self,
        event_bus: EventBus,
    ) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            ),
            event_bus=event_bus,
        )

    async def on_start(self) -> None:
        pass

    async def on_stop(self) -> None:
        pass


@pytest.mark.asyncio
async def test_service_events() -> None:
    """
    Starting and stopping a service should publish
    lifecycle events to the shared EventBus.
    """

    event_bus = EventBus()

    started: list[dict[str, Any]] = []
    stopped: list[dict[str, Any]] = []

    event_bus.subscribe(
        "service.started",
        lambda payload: started.append(payload),
    )

    event_bus.subscribe(
        "service.stopped",
        lambda payload: stopped.append(payload),
    )

    service = DummyService(event_bus)

    #
    # Start.
    #
    await service.start()

    assert len(started) == 1
    assert started[0]["service"] == "dummy-service"

    #
    # Stop.
    #
    await service.stop()

    assert len(stopped) == 1
    assert stopped[0]["service"] == "dummy-service"

    #
    # EventBus diagnostics.
    #
    diagnostics = cast(
        Mapping[str, Any],
        event_bus.diagnostics(),
    )

    subscriptions = cast(
        Mapping[str, int],
        diagnostics["subscriptions"],
    )

    assert subscriptions["service.started"] == 1
    assert subscriptions["service.stopped"] == 1