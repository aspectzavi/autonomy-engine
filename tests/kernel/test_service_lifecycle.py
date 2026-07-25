"""
KernelService lifecycle tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.lifecycle import LifecycleState
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Service used for lifecycle state testing.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            ),
        )

    async def on_start(self) -> None:
        pass

    async def on_stop(self) -> None:
        pass


@pytest.mark.asyncio
async def test_service_lifecycle() -> None:
    """
    Verify lifecycle state transitions across the
    complete service lifecycle.
    """

    service = DummyService()

    #
    # Initial state.
    #
    state = service.lifecycle.state

    assert (
        state
        is LifecycleState.INITIALIZED
    )

    #
    # Start.
    #
    await service.start()

    state = service.lifecycle.state

    assert (
        state
        is LifecycleState.RUNNING
    )

    assert service.is_running

    #
    # Restart.
    #
    await service.restart()

    state = service.lifecycle.state

    assert (
        state
        is LifecycleState.RUNNING
    )

    assert service.is_running

    #
    # Stop.
    #
    await service.stop()

    state = service.lifecycle.state

    assert (
        state
        is LifecycleState.STOPPED
    )

    assert not service.is_running