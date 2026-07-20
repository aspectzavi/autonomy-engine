"""
Kernel application.

The Application is the top-level runtime owner.

Responsibilities:

- initialize kernel runtime
- control application lifecycle
- expose diagnostics

Service construction belongs to KernelBootstrap.
Service execution belongs to Runtime.
"""

from __future__ import annotations

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.runtime import Runtime
from backend.core.observability.container import (
    ObservabilityContainer,
)


class Application:
    """
    Main kernel application.
    """

    def __init__(
        self,
        bootstrap: KernelBootstrap | None = None,
    ) -> None:
        self._bootstrap = (
            bootstrap
            or KernelBootstrap()
        )

        self._runtime: Runtime | None = None

        self._started = False

        self._observability = ObservabilityContainer()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def bootstrap(self) -> KernelBootstrap:
        """
        Return bootstrap instance.
        """
        return self._bootstrap

    @property
    def runtime(self) -> Runtime:
        """
        Return runtime instance.
        """
        if self._runtime is None:
            self._runtime = self._bootstrap.build()

        return self._runtime

    @property
    def is_running(self) -> bool:
        """
        Whether application is running.
        """
        return self._started
    
    @property
    def observability(
        self,
    ) -> ObservabilityContainer:
        """
        Shared observability services.
        """
        return self._observability

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """
        Start application runtime.
        """

        if self._started:
            return

        await self.runtime.start()

        self._started = True

    async def stop(self) -> None:
        """
        Stop application runtime.
        """

        if not self._started:
            return

        await self.runtime.stop()

        self._started = False

    async def restart(self) -> None:
        """
        Restart application runtime.
        """

        await self.stop()

        await self.start()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return application diagnostics.
        """

        return {
            "running": self._started,
            "runtime": self.runtime.diagnostics(),
            "observability": {
                "events": self.observability.events.diagnostics(),
            },
        }