"""
KernelService start tests.
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

    async def on_start(self) -> None:
        self.started = True


@pytest.mark.asyncio
async def test_service_start() -> None:
    """
    Starting a service should transition it into the
    RUNNING lifecycle state and update runtime metadata.
    """

    service = DummyService()

    #
    # Initial state.
    #
    assert not service.is_running
    assert service.started is False

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    assert (
        diagnostics["lifecycle"]
        == LifecycleState.INITIALIZED.value
    )

    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "initialized"

    #
    # Start service.
    #
    await service.start()

    assert service.started is True
    assert service.is_running

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    #
    # Lifecycle.
    #
    assert (
        diagnostics["lifecycle"]
        == LifecycleState.RUNNING.value
    )

    #
    # Runtime.
    #
    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "running"

    #
    # Health.
    #
    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    # Verify the service reports a running/healthy status
    # without depending on optional implementation fields.
    assert "status" in health
    assert health["status"] == "running"

    #
    # Metadata.
    #
    metadata = cast(
        Mapping[str, Any],
        diagnostics["metadata"],
    )

    assert metadata["name"] == "dummy-service"
    assert metadata["version"] == "1.0.0"