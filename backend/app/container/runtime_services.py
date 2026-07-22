"""
Kernel service registration.

Registers runtime-managed services into the dependency injection
container.
"""

from __future__ import annotations

from backend.app.container.container import Container


from backend.core.observability.events import EventBus
from backend.core.observability.tracing import Tracing

from backend.core.services.agent_service import AgentService
from backend.core.services.tool_service import ToolService
from backend.core.services.workflow_service import WorkflowService

from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_pipeline import ExecutionPipeline
from backend.core.runtime.middleware_registry import MiddlewareRegistry
from backend.core.observability.logger import KernelLogger

def register_runtime_services(
    container: Container,
) -> None:
    """
    Register runtime-managed services.
    """

    #
    # Core application services
    #

    if not container.contains(
        ToolService,
    ):
        container.register_singleton(
            ToolService,
        )

    if not container.contains(
        AgentService,
    ):
        container.register_singleton(
            AgentService,
        )

    if not container.contains(
        WorkflowService,
    ):
        container.register_singleton(
            WorkflowService,
        )


    #
    # Observability services
    #

    if not container.contains(
        EventBus,
    ):
        container.register_singleton(
            EventBus,
        )

    if not container.contains(
        Tracing,
    ):
        container.register_singleton(
            Tracing,
        )

        #
    # Logging services
    #

    if not container.contains(
        KernelLogger,
    ):
        container.register_singleton(
            KernelLogger,
        )    


    #
    # Runtime execution infrastructure
    #

    if not container.contains(
        ExecutionEngine,
    ):
        container.register_singleton(
            ExecutionEngine,
        )

    if not container.contains(
        MiddlewareRegistry,
    ):
        container.register_singleton(
            MiddlewareRegistry,
        )

    if not container.contains(
        ExecutionPipeline,
    ):
        container.register_singleton(
            ExecutionPipeline,
        )