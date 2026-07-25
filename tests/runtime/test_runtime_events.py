"""
Runtime event propagation tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap


@pytest.mark.asyncio
async def test_runtime_events() -> None:
    """
    Runtime services should publish lifecycle events to the
    shared EventBus during startup and shutdown.
    """

    bootstrap = KernelBootstrap()

    runtime = bootstrap.build()

    event_bus = bootstrap.events

    #
    # Runtime should use the shared EventBus.
    #
    assert runtime.context.events is event_bus

    started_events: list[dict[str, Any]] = []
    stopped_events: list[dict[str, Any]] = []

    #
    # Subscribe before runtime starts.
    #
    event_bus.subscribe(
        "service.started",
        started_events.append,
    )

    event_bus.subscribe(
        "service.stopped",
        stopped_events.append,
    )

    service_names = {
        service.metadata.name
        for service in runtime.services()
    }

    #
    # Start runtime.
    #
    await runtime.start()

    assert runtime.is_running

    assert len(started_events) == len(service_names)

    assert {
        event["service"]
        for event in started_events
    } == service_names

    #
    # Stop runtime.
    #
    await runtime.stop()

    assert not runtime.is_running

    assert len(stopped_events) == len(service_names)

    assert {
        event["service"]
        for event in stopped_events
    } == service_names

    #
    # EventBus diagnostics should reflect subscriptions.
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