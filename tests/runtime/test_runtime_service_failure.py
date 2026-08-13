from __future__ import annotations

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import ServiceRegistration
from backend.core.kernel.runtime_state import RuntimeState
from backend.core.kernel.service import KernelService
from backend.core.kernel.exceptions import LifecycleError

class FailingService(KernelService):
    """
    Service that always fails during startup.
    """

    def __init__(self) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="failing-service",
                version="1.0.0",
                description="Runtime startup failure test.",
            ),
        )

    async def on_start(self) -> None:
        raise RuntimeError("Startup failed.")

    async def on_stop(self) -> None:
        return


@pytest.mark.asyncio
async def test_runtime_service_failure() -> None:
    """
    Runtime should enter FAILED state when a service
    throws during startup.
    """

    bootstrap = KernelBootstrap()

    #
    # Register the failing service.
    #
    bootstrap.register(
        ServiceRegistration(
            metadata=FailingService().metadata,
            service=FailingService(),
        )
    )

    runtime = bootstrap.build()

    with pytest.raises(
        LifecycleError,
        match="Failed to start service 'failing-service'",
    ):
        await runtime.start()

    assert runtime.state is RuntimeState.FAILED
    assert not runtime.is_running

    diagnostics = runtime.diagnostics()

    assert diagnostics["state"] == "failed"
    assert diagnostics["is_running"] is False