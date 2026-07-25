"""
KernelService locking tests.
"""

from __future__ import annotations

import asyncio

import pytest

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class SlowService(KernelService):
    """
    Service that records how many times its startup hook runs.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="slow-service",
                version="1.0.0",
            ),
        )

        self.start_calls = 0
        self.stop_calls = 0

    async def on_start(self) -> None:
        self.start_calls += 1
        await asyncio.sleep(0.05)

    async def on_stop(self) -> None:
        self.stop_calls += 1
        await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_service_locking() -> None:
    """
    Concurrent lifecycle requests should be serialized
    by the internal lifecycle lock.
    """

    service = SlowService()

    #
    # Two concurrent starts.
    #
    await asyncio.gather(
        service.start(),
        service.start(),
    )

    #
    # on_start() should execute only once.
    #
    assert service.start_calls == 1
    assert service.is_running

    #
    # Two concurrent stops.
    #
    await asyncio.gather(
        service.stop(),
        service.stop(),
    )

    #
    # on_stop() should execute only once.
    #
    assert service.stop_calls == 1
    assert not service.is_running