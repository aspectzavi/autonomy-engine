"""
Kernel runtime.

The Runtime is responsible for orchestrating the lifecycle of all
kernel-managed services.

Responsibilities:

- validate the dependency graph
- start services
- stop services
- restart the runtime
- expose diagnostics

The Runtime owns orchestration only. Service implementation remains
inside KernelService.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.core.kernel.dependency_graph import DependencyGraph
from backend.core.kernel.registry import ServiceRegistry
from backend.core.kernel.runtime_state import RuntimeState
from backend.core.kernel.service import KernelService
from backend.core.kernel.runtime_context import RuntimeContext
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger


class Runtime:
    """
    Kernel runtime.

    Orchestrates the lifecycle of all registered services.
    """

    def __init__(
        self,
        registry: ServiceRegistry,
        dependency_graph: DependencyGraph,
        *,
        container: Container,
        logger: KernelLogger,
        events: EventBus,
    ) -> None:
        self._registry = registry
        self._graph = dependency_graph

        self._container = container
        self._logger = logger
        self._events = events

        self._state = RuntimeState.CREATED

        self._context = RuntimeContext(
            runtime=self,
            container=self._container,
            logger=self._logger,
            events=self._events,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(
        self,
    ) -> ServiceRegistry:
        """
        Service registry.
        """
        return self._registry

    @property
    def dependency_graph(
        self,
    ) -> DependencyGraph:
        """
        Dependency graph.
        """
        return self._graph

    @property
    def context(
        self,
    ) -> RuntimeContext:
        """
        Shared runtime context.
        """
        return self._context

    @property
    def state(
        self,
    ) -> RuntimeState:
        """
        Current runtime state.
        """
        return self._state

    @property
    def is_running(
        self,
    ) -> bool:
        """
        Whether the runtime is currently running.
        """
        return self._state is RuntimeState.RUNNING

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
    ) -> None:
        """
        Start the runtime.
        """

        if self.is_running:
            return

        self._state = RuntimeState.STARTING

        try:
            self.validate()

            for service_name in self._graph.startup_order():
                service = self._registry.get(
                    service_name,
                )

                await service.start()

            self._state = RuntimeState.RUNNING

        except Exception:
            self._state = RuntimeState.FAILED
            raise

    async def stop(
        self,
    ) -> None:
        """
        Stop the runtime.
        """

        if self._state in (
            RuntimeState.STOPPED,
            RuntimeState.CREATED,
        ):
            return

        self._state = RuntimeState.STOPPING

        try:
            for service_name in self._graph.shutdown_order():
                service = self._registry.get(
                    service_name,
                )

                await service.stop()

            self._state = RuntimeState.STOPPED

        except Exception:
            self._state = RuntimeState.FAILED
            raise

    async def restart(
        self,
    ) -> None:
        """
        Restart the runtime.
        """

        await self.stop()
        await self.start()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
    ) -> None:
        """
        Validate runtime configuration.
        """

        self._registry.validate()
        self._graph.validate()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime diagnostics.
        """

        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "service_count": len(
                self._registry,
            ),
            "startup_order": (
                self._graph.startup_order()
            ),
            "shutdown_order": (
                self._graph.shutdown_order()
            ),
            "registry": (
                self._registry.diagnostics()
            ),
            "dependency_graph": (
                self._graph.diagnostics()
            ),
            "context": {
                "available": self.context is not None,
                "container": (
                    self.context.container.diagnostics()
                    if self.context is not None
                    else None
                ),
                "events": (
                    self.context.events.diagnostics()
                    if self.context is not None
                    else None
                ),
                "logger": (
                    type(
                        self.context.logger,
                    ).__name__
                    if self.context is not None
                    else None
                ),
            },
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def services(
        self,
    ) -> tuple[KernelService, ...]:
        """
        Return all registered services.
        """

        return self._registry.services()