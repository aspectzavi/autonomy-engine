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

from backend.app.container.container import Container
from backend.app.container.agent_factory import (
    create_agent_factory,
)

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.runtime import Runtime
from backend.core.observability.container import (
    ObservabilityContainer,
)
from backend.core.config.config import EngineConfig


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

        self._bootstrap.wire_agents()

        create_agent_factory(
            self.container,
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
    def container(
        self,
    ) -> Container:
        """
        Return the dependency injection container.
        """
        return self.bootstrap.container   
    
    @property
    def config(
        self,
    ) -> EngineConfig:
        """
        Return the shared engine configuration.
        """
        return self.bootstrap.config    

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
        
        runtime = self.runtime

        await runtime.start()

        self._started = True

    async def stop(self) -> None:
        """
        Stop application runtime.
        """

        if not self._started:
            return
        
        runtime = self.runtime

        await runtime.stop()

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
            "running": self.is_running,
            "configuration": (
                self.config.diagnostics()
            ),
            "runtime": (
                self.runtime.diagnostics()
            ),
            "observability": {
                "events": (
                    self.observability.events.diagnostics()
                ),
            },
        }