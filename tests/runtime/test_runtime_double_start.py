"""
Runtime double-start tests.
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.runtime_state import RuntimeState


@pytest.mark.asyncio
async def test_runtime_double_start() -> None:
    """
    Starting an already-running runtime should be a no-op.
    """

    bootstrap = KernelBootstrap()
    runtime = bootstrap.build()

    #
    # First start.
    #
    await runtime.start()

    diagnostics_before = cast(
        dict[str, Any],
        runtime.diagnostics(),
    )

    registry_before = cast(
        dict[str, Any],
        diagnostics_before["registry"],
    )

    #
    # Second start should not restart services.
    #
    await runtime.start()

    diagnostics_after = cast(
        dict[str, Any],
        runtime.diagnostics(),
    )

    registry_after = cast(
        dict[str, Any],
        diagnostics_after["registry"],
    )

    #
    # Runtime remains healthy.
    #
    state = runtime.state

    assert runtime.is_running
    assert state is RuntimeState.RUNNING

    #
    # Diagnostics remain unchanged.
    #
    assert diagnostics_after["state"] == "running"
    assert diagnostics_after["is_running"] is True
    assert (
        diagnostics_after["service_count"]
        == diagnostics_before["service_count"]
    )

    assert (
        registry_after["service_count"]
        == registry_before["service_count"]
    )

    assert (
        registry_after["services"]
        == registry_before["services"]
    )

    #
    # Cleanup.
    #
    await runtime.stop()

    state = runtime.state

    assert state is RuntimeState.STOPPED