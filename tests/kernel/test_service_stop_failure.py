"""
KernelService stop failure tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.exceptions import LifecycleError
from backend.core.kernel.lifecycle import LifecycleState
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class FailingStopService(KernelService):
    """
    Service whose shutdown always fails.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="failing-stop-service",
                version="1.0.0",
            ),
        )

        self.started = False
        self.stopped = False

    async def on_start(self) -> None:
        self.started = True

    async def on_stop(self) -> None:
        self.stopped = True
        raise RuntimeError("Shutdown failed.")


@pytest.mark.asyncio
async def test_service_stop_failure() -> None:
    """
    A shutdown failure should transition the service
    into the FAILED lifecycle state and raise a
    LifecycleError.
    """

    service = FailingStopService()

    #
    # Start successfully.
    #
    await service.start()

    assert service.is_running
    assert service.started is True

    #
    # Stop should fail.
    #
    with pytest.raises(
        LifecycleError,
        match="Failed to stop service 'failing-stop-service'",
    ):
        await service.stop()

    #
    # Shutdown hook was entered.
    #
    assert service.stopped is True

    #
    # Service should no longer report RUNNING.
    #
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
        == LifecycleState.FAILED.value
    )

    #
    # Runtime should still reflect shutdown in progress.
    #
    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "stopping"

    #
    # Health.
    #
    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    assert health["status"] == "failed"

    #
    # Metadata.
    #
    metadata = cast(
        Mapping[str, Any],
        diagnostics["metadata"],
    )

    assert metadata["name"] == "failing-stop-service"
    assert metadata["version"] == "1.0.0"