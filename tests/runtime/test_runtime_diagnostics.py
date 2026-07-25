"""
Runtime diagnostics tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap


@pytest.mark.asyncio
async def test_runtime_diagnostics() -> None:
    """
    Runtime diagnostics should accurately reflect the
    runtime lifecycle and registered services.
    """

    bootstrap = KernelBootstrap()

    runtime = bootstrap.build()

    #
    # Before startup.
    #
    diagnostics = cast(
        Mapping[str, Any],
        runtime.diagnostics(),
    )

    assert diagnostics["state"] == "created"
    assert diagnostics["is_running"] is False

    service_count = cast(
        int,
        diagnostics["service_count"],
    )

    assert service_count == len(runtime.services())

    registry = cast(
        Mapping[str, Any],
        diagnostics["registry"],
    )

    assert registry["service_count"] == service_count

    dependency_graph = cast(
        Mapping[str, Any],
        diagnostics["dependency_graph"],
    )

    startup_order = cast(
        tuple[str, ...],
        dependency_graph["startup_order"],
    )

    shutdown_order = cast(
        tuple[str, ...],
        dependency_graph["shutdown_order"],
    )

    assert len(startup_order) == service_count
    assert len(shutdown_order) == service_count

    context = cast(
        Mapping[str, Any],
        diagnostics["context"],
    )

    assert context["available"] is True
    assert context["logger"] == "KernelLogger"

    #
    # After startup.
    #
    await runtime.start()

    diagnostics = cast(
        Mapping[str, Any],
        runtime.diagnostics(),
    )

    assert diagnostics["state"] == "running"
    assert diagnostics["is_running"] is True

    #
    # After shutdown.
    #
    await runtime.stop()

    diagnostics = cast(
        Mapping[str, Any],
        runtime.diagnostics(),
    )

    assert diagnostics["state"] == "stopped"
    assert diagnostics["is_running"] is False

    #
    # Service count should remain constant.
    #
    assert diagnostics["service_count"] == service_count

    registry = cast(
        Mapping[str, Any],
        diagnostics["registry"],
    )

    assert registry["service_count"] == service_count