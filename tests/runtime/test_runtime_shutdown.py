"""
Runtime shutdown tests.

Validates graceful runtime shutdown.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.bootstrap import (
    KernelBootstrap,
)


@pytest.mark.asyncio
async def test_runtime_shutdown() -> None:
    """
    Validate graceful runtime shutdown.
    """

    bootstrap = KernelBootstrap()

    runtime = bootstrap.build()

    #
    # Start runtime.
    #
    await runtime.start()

    assert runtime.is_running

    #
    # Shutdown runtime.
    #
    await runtime.stop()

    assert not runtime.is_running

    diagnostics = runtime.diagnostics()

    assert runtime.is_running is False

    diagnostics = runtime.diagnostics()

    assert diagnostics["is_running"] is False
    assert diagnostics["state"] == "stopped"
    assert diagnostics["service_count"] == 3
    assert diagnostics["shutdown_order"] == (
        "workflow-service",
        "tool-service",
        "agent-service",
    )