"""
Runtime service registration tests.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.app.container.runtime_services import (
    register_runtime_services,
)
from backend.core.memory.memory_store import (
    MemoryStore,
)
from backend.core.observability.events import (
    EventBus,
)
from backend.core.observability.logger import (
    KernelLogger,
)
from backend.core.observability.tracing import (
    Tracing,
)
from backend.core.runtime.execution_engine import (
    ExecutionEngine,
)
from backend.core.runtime.execution_pipeline import (
    ExecutionPipeline,
)
from backend.core.services.agent_service import (
    AgentService,
)
from backend.core.services.memory_service import (
    MemoryService,
)
from backend.core.services.task_service import (
    TaskService,
)
from backend.core.services.tool_service import (
    ToolService,
)
from backend.core.services.workflow_service import (
    WorkflowService,
)


def test_runtime_services() -> None:
    """
    register_runtime_services() should register every
    runtime-managed singleton exactly once.
    """

    container = Container()

    register_runtime_services(
        container,
    )

    # ------------------------------------------------------------------
    # Core services
    # ------------------------------------------------------------------

    assert container.contains(
        ToolService,
    )

    assert container.contains(
        AgentService,
    )

    assert container.contains(
        TaskService,
    )

    assert container.contains(
        WorkflowService,
    )

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    assert container.contains(
        EventBus,
    )

    assert container.contains(
        Tracing,
    )

    assert container.contains(
        KernelLogger,
    )

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    assert container.contains(
        ExecutionEngine,
    )

    assert container.contains(
        ExecutionPipeline,
    )

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    assert container.contains(
        MemoryStore,
    )

    assert container.contains(
        MemoryService,
    )

    # ------------------------------------------------------------------
    # Idempotency
    # ------------------------------------------------------------------

    count = len(
        container,
    )

    register_runtime_services(
        container,
    )

    assert len(
        container,
    ) == count

    diagnostics = container.diagnostics()

    assert diagnostics[
        "service_count"
    ] == count