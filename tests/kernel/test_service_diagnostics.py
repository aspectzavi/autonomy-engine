"""
KernelService diagnostics tests.
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
    Service used for diagnostics testing.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.2.3",
            ),
        )

    async def on_start(self) -> None:
        pass

    async def on_stop(self) -> None:
        pass


@pytest.mark.asyncio
async def test_service_diagnostics() -> None:
    """
    Diagnostics should remain internally consistent
    throughout the service lifecycle.
    """

    service = DummyService()

    #
    # Before startup.
    #
    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    #
    # Top-level keys.
    #
    assert set(diagnostics) == {
        "metadata",
        "health",
        "runtime",
        "lifecycle",
    }

    metadata = cast(
        Mapping[str, Any],
        diagnostics["metadata"],
    )

    assert metadata["name"] == "dummy-service"
    assert metadata["version"] == "1.2.3"

    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "initialized"

    assert (
        diagnostics["lifecycle"]
        == LifecycleState.INITIALIZED.value
    )

    #
    # After start.
    #
    await service.start()

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
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

    assert "status" in health
    assert health["status"] == "running"

    assert (
        diagnostics["lifecycle"]
        == LifecycleState.RUNNING.value
    )

    #
    # After stop.
    #
    await service.stop()

    diagnostics = cast(
        Mapping[str, Any],
        service.diagnostics(),
    )

    runtime = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime["state"] == "stopped"

    assert (
        diagnostics["lifecycle"]
        == LifecycleState.STOPPED.value
    )

    #
    # Metadata should never change.
    #
    metadata = cast(
        Mapping[str, Any],
        diagnostics["metadata"],
    )

    assert metadata["name"] == "dummy-service"
    assert metadata["version"] == "1.2.3"