"""
Runtime double-stop tests.
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.runtime_state import RuntimeState


@pytest.mark.asyncio
async def test_runtime_double_stop() -> None:
    """
    Stopping an already-stopped runtime should be a no-op.
    """

    bootstrap = KernelBootstrap()
    runtime = bootstrap.build()

    #
    # Start the runtime.
    #
    await runtime.start()

    assert runtime.state is RuntimeState.RUNNING
    assert runtime.is_running

    #
    # First stop.
    #
    await runtime.stop()

    diagnostics_before = cast(
        dict[str, Any],
        runtime.diagnostics(),
    )

    registry_before = cast(
        dict[str, Any],
        diagnostics_before["registry"],
    )

    #
    # Second stop should do nothing.
    #
    await runtime.stop()

    diagnostics_after = cast(
        dict[str, Any],
        runtime.diagnostics(),
    )

    registry_after = cast(
        dict[str, Any],
        diagnostics_after["registry"],
    )

    #
    # Runtime remains stopped.
    #
    assert diagnostics_after["state"] == "stopped"
    assert diagnostics_after["is_running"] is False
    assert not runtime.is_running

    #
    # Diagnostics remain unchanged.
    #
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