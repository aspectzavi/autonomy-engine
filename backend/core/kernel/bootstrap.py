"""
Kernel bootstrap.

The bootstrap is the kernel composition root.

Responsibilities:

- create dependency injection container
- wire application services
- create kernel registry
- create dependency graph
- create runtime

It is responsible for construction only.
Execution belongs to Runtime/Application.
"""

from __future__ import annotations

from typing import Any

from backend.app.container.container import Container
from backend.app.container.wiring import ContainerWiring
from backend.app.container.agents import register_agents

from backend.core.kernel.dependency_graph import DependencyGraph
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.runtime import Runtime
from backend.core.kernel.service import KernelService
from backend.core.observability.events import EventBus
from backend.core.observability.tracing import Tracing
from backend.core.observability.logger import KernelLogger
from backend.core.config.config import EngineConfig
from backend.core.config.loader import ConfigurationLoader
from backend.core.services.tool_service import ToolService
from backend.core.services.agent_service import (
    AgentService,
)
from backend.core.services.workflow_service import (
    WorkflowService,
)
from backend.app.container.runtime_services import (
    register_runtime_services,
)
from backend.core.kernel.runtime_context import (
    RuntimeContext,
)


class KernelBootstrap:
    """
    Bootstrapper for kernel runtime.

    Acts as the composition root.
    """

    def __init__(
        self,
        *,
        configuration_loader: ConfigurationLoader | None = None,
    ) -> None:
        self._configuration_loader = (
            configuration_loader
            or ConfigurationLoader()
        )

        self._config = (
            self._configuration_loader.load()
        )

        self._events = EventBus()

        self._logger = KernelLogger()

        self._tracing = Tracing()

        self._container = Container()

        register_runtime_services(
            self._container,
        )

        self._container.register_instance(
            EngineConfig,
            self._config,
        )

        self._tool_service = (
            self._container.resolve(
                ToolService,
            )
        )

        self._agent_service = (
            self._container.resolve(
                AgentService,
            )
        )

        self._workflow_service = (
            self._container.resolve(
                WorkflowService,
            )
        )

        self._wiring = ContainerWiring(
            self._container,
        )

        self._registry = ServiceRegistry()

        self._graph = DependencyGraph(
            self._registry,
        )

        self._runtime = Runtime(
            registry=self._registry,
            dependency_graph=self._graph,
            container=self._container,
            logger=self._container.resolve(
                KernelLogger,
            ),
            events=self._events,
        )

        self._runtime_context = RuntimeContext(
            runtime=self._runtime,
            container=self._container,
            logger=self._logger,
            events=self._events,
        )

        self._container.register_instance(
            RuntimeContext,
            self._runtime_context,
        )

        self._container.register_instance(
            KernelLogger,
            self._logger,
        )

        self.register_service(
            self._tool_service,
        )

        self.register_service(
            self._agent_service,
        )

        self.register_service(
            self._workflow_service,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def container(self) -> Container:
        """
        Return application dependency container.
        """
        return self._container

    @property
    def registry(self) -> ServiceRegistry:
        """
        Return kernel service registry.
        """
        return self._registry

    @property
    def dependency_graph(self) -> DependencyGraph:
        """
        Return dependency graph.
        """
        return self._graph

    @property
    def runtime(self) -> Runtime:
        """
        Return kernel runtime.
        """
        return self._runtime
    
    @property
    def configuration_loader(
        self,
    ) -> ConfigurationLoader:
        """
        Return the configuration loader.
        """
        return self._configuration_loader


    @property
    def config(
        self,
    ) -> EngineConfig:
        """
        Return the engine configuration.
        """
        return self._config
    
    @property
    def events(self) -> EventBus:
        """
        Shared kernel event bus.
        """
        return self._events

    @property
    def tracing(self) -> Tracing:
        """
        Shared runtime tracing service.
        """
        return self._tracing

    @property
    def runtime_context(
        self,
    ) -> RuntimeContext:
        """
        Shared runtime execution context.
        """
        return self._runtime_context
    
    @property
    def tool_service(
        self,
    ) -> ToolService:
        """
        Return the runtime tool service.
        """
        return self._tool_service
    
    @property
    def agent_service(
        self,
    ) -> AgentService:
        """
        Return the runtime agent service.
        """
        return self._agent_service

    @property
    def workflow_service(
        self,
    ) -> WorkflowService:
        """
        Return the runtime workflow service.
        """
        return self._workflow_service

    # ------------------------------------------------------------------
    # DI Wiring
    # ------------------------------------------------------------------

    def wire(
        self,
        services: list[type[Any]],
    ) -> "KernelBootstrap":
        """
        Register decorated dependency services.
        """

        self._wiring.register_services(
            services
        )

        return self
    
    def wire_agents(
        self,
    ) -> "KernelBootstrap":
        """
        Register agent infrastructure.
        """

        register_agents(
            self._container,
        )

        return self    

    # ------------------------------------------------------------------
    # Kernel Registration
    # ------------------------------------------------------------------

    def register(
        self,
        registration: ServiceRegistration,
    ) -> "KernelBootstrap":
        """
        Register a kernel service.
        """

        self._registry.register(
            registration
        )

        return self

    def register_service(
        self,
        service: KernelService,
    ) -> "KernelBootstrap":
        """
        Register a kernel service instance.
        """
        service._events = self._events

        registration = ServiceRegistration(
            metadata=service.metadata,
            service=service,
        )

        self._registry.register(
            registration
        )

        return self

    # ------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------

    def depends_on(
        self,
        service: str,
        *dependencies: str,
    ) -> "KernelBootstrap":
        """
        Define service dependencies.
        """

        self._graph.add(
            service,
            *dependencies,
        )

        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> Runtime:
        """
        Validate and return runtime.
        """

        self._registry.validate()

        self._graph.validate()

        return self._runtime

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return bootstrap diagnostics.
        """

        return {
            "configuration": (
                self.config.diagnostics()
            ),
            "container": (
                self.container.diagnostics()
            ),
            "registry": (
                self.registry.diagnostics()
            ),
            "dependency_graph": (
                self.dependency_graph.diagnostics()
            ),
            "runtime": (
                self.runtime.diagnostics()
            ),
            "tool_service": (
                self.tool_service.diagnostics()
            ),
            "agent_service": (
                self.agent_service.diagnostics()
            ),
            "workflow_service": (
                self.workflow_service.diagnostics()
            ),
            "tracing": (
                self.tracing.diagnostics()
            ),
            "runtime_context": (
                self.runtime_context.diagnostics()
            ),
        }
        
        