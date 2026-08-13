"""
Runtime context tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.runtime_context import RuntimeContext


@pytest.mark.asyncio
async def test_runtime_context() -> None:
    """
    The runtime should expose a fully initialized
    RuntimeContext throughout its lifecycle.
    """

    bootstrap = KernelBootstrap()

    runtime = bootstrap.build()

    context = runtime.context

    #
    # Basic wiring.
    #
    assert isinstance(context, RuntimeContext)

    assert context.runtime is runtime
    assert context.container is bootstrap.container
    assert context.events is bootstrap.events
    assert context.logger is bootstrap.runtime_context.logger

    #
    # Context should exist before startup.
    #
    diagnostics = cast(
        Mapping[str, Any],
        context.diagnostics(),
    )

    runtime_diag = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    container_diag = cast(
        Mapping[str, Any],
        diagnostics["container"],
    )

    assert runtime_diag["state"] == "created"
    assert isinstance(container_diag["service_count"], int)
    assert container_diag["service_count"] > 0

    #
    # Start runtime.
    #
    await runtime.start()

    diagnostics = cast(
        Mapping[str, Any],
        context.diagnostics(),
    )

    runtime_diag = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime_diag["state"] == "running"
    assert runtime.is_running

    #
    # Stop runtime.
    #
    await runtime.stop()

    diagnostics = cast(
        Mapping[str, Any],
        context.diagnostics(),
    )

    runtime_diag = cast(
        Mapping[str, Any],
        diagnostics["runtime"],
    )

    assert runtime_diag["state"] == "stopped"
    assert not runtime.is_running

    #
    # Context instance should never change.
    #
    assert runtime.context is context