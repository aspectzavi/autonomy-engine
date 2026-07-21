"""
Kernel service registration.

Registers runtime-managed services into the dependency injection
container.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.core.services.agent_service import AgentService
from backend.core.services.tool_service import ToolService
from backend.core.services.workflow_service import WorkflowService


def register_runtime_services(
    container: Container,
) -> None:
    """
    Register runtime-managed services.
    """

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