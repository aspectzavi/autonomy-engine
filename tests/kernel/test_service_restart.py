"""
KernelService restart tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.lifecycle import LifecycleState
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Service used to verify restart behaviour.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            ),
        )

        self.start_count = 0
        self.stop_count = 0
        self.restart_count = 0

    async def on_start(self) -> None:
        self.start_count += 1

    async def on_stop(self) -> None:
        self.stop_count += 1

    async def on_restart(self) -> None:
        self.restart_count += 1


@pytest.mark.asyncio
async def test_service_restart() -> None:
    """
    Restarting a service should invoke stop,
    restart and start hooks in order while
    leaving the service running afterwards.
    """

    service = DummyService()

    #
    # Initial start.
    #
    await service.start()

    assert service.is_running
    assert service.start_count == 1
    assert service.stop_count == 0
    assert service.restart_count == 0

    #
    # Restart.
    #
    await service.restart()

    assert service.is_running

    #
    # Restart should have stopped then started again.
    #
    assert service.start_count == 2
    assert service.stop_count == 1
    assert service.restart_count == 1

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    assert (
        diagnostics["lifecycle"]
        == LifecycleState.RUNNING.value
    )

    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "running"

    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    assert health["status"] == "running"

    metadata = cast(
        Mapping[str, Any],
        diagnostics["metadata"],
    )

    assert metadata["name"] == "dummy-service"
    assert metadata["version"] == "1.0.0"