"""
KernelService stop tests.
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
    Simple service used for lifecycle testing.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            ),
        )

        self.started = False
        self.stopped = False

    async def on_start(self) -> None:
        self.started = True

    async def on_stop(self) -> None:
        self.stopped = True


@pytest.mark.asyncio
async def test_service_stop() -> None:
    """
    Stopping a running service should transition it into the
    STOPPED lifecycle state and update runtime metadata.
    """

    service = DummyService()

    #
    # Start first.
    #
    await service.start()

    assert service.is_running
    assert service.started is True
    assert service.stopped is False

    #
    # Stop.
    #
    await service.stop()

    assert service.stopped is True
    assert not service.is_running

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    #
    # Lifecycle.
    #
    assert (
        diagnostics["lifecycle"]
        == LifecycleState.STOPPED.value
    )

    #
    # Runtime.
    #
    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "stopped"

    #
    # Health.
    #
    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    assert "status" in health

    #
    # Metadata remains unchanged.
    #
    metadata = cast(
        Mapping[str, Any],
        diagnostics["metadata"],
    )

    assert metadata["name"] == "dummy-service"
    assert metadata["version"] == "1.0.0"