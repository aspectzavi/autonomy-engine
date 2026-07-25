"""
KernelService start failure tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.exceptions import LifecycleError
from backend.core.kernel.lifecycle import LifecycleState
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class FailingService(KernelService):
    """
    Service whose startup always fails.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="failing-service",
                version="1.0.0",
            ),
        )

        self.started = False

    async def on_start(self) -> None:
        self.started = True
        raise RuntimeError("Startup failed.")


@pytest.mark.asyncio
async def test_service_start_failure() -> None:
    """
    A startup failure should transition the service
    into the FAILED lifecycle state and raise a
    LifecycleError.
    """

    service = FailingService()

    with pytest.raises(
        LifecycleError,
        match="Failed to start service 'failing-service'",
    ):
        await service.start()

    #
    # Startup hook was entered.
    #
    assert service.started is True

    #
    # Service should not be running.
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
    # Runtime.
    #
    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    #
    # Runtime never reaches RUNNING.
    #
    assert runtime["state"] == "starting"

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

    assert metadata["name"] == "failing-service"
    assert metadata["version"] == "1.0.0"