"""
Runtime boot smoke tests.

Validates that the autonomy engine kernel can initialize,
start services, and shut down cleanly.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.bootstrap import (
    KernelBootstrap,
)


@pytest.mark.asyncio
async def test_runtime_boot() -> None:
    """
    Validate kernel runtime lifecycle.
    """

    bootstrap = KernelBootstrap()

    runtime = bootstrap.build()

    await runtime.start()

    diagnostics = runtime.diagnostics()

    assert diagnostics["is_running"] is True

    await runtime.stop()

    diagnostics = runtime.diagnostics()

    assert diagnostics["is_running"] is False