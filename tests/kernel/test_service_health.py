"""
KernelService health tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.exceptions import LifecycleError
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class HealthyService(KernelService):
    """
    Service that starts and stops normally.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="healthy-service",
                version="1.0.0",
            ),
        )

    async def on_start(self) -> None:
        pass

    async def on_stop(self) -> None:
        pass


class FailingService(KernelService):
    """
    Service whose startup fails.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="failing-service",
                version="1.0.0",
            ),
        )

    async def on_start(self) -> None:
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_service_health() -> None:
    """
    Health diagnostics should reflect successful and
    failed lifecycle transitions.
    """

    #
    # Healthy service.
    #
    service = HealthyService()

    await service.start()

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    assert "status" in health
    assert health["status"] == "running"

    await service.stop()

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    #
    # We don't enforce the exact stopped status because
    # implementations may represent it differently.
    #
    assert "status" in health

    #
    # Failed service.
    #
    failing = FailingService()

    with pytest.raises(LifecycleError):
        await failing.start()

    diagnostics = cast(
        Mapping[str, Any],
        failing.diagnostics(),
    )

    health = cast(
        Mapping[str, Any],
        diagnostics["health"],
    )

    assert health["status"] == "failed"