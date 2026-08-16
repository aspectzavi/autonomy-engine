"""
Kernel service registration.

Registers runtime-managed services into the dependency injection
container.
"""

from __future__ import annotations

from typing import Any
from typing import cast

from backend.app.container.container import Container

from backend.core.memory.embedding_provider import (
    EmbeddingProvider,
)
from backend.core.memory.embedding_service import (
    EmbeddingService,
)
from backend.core.memory.hashing_embedding_provider import (
    HashingEmbeddingProvider,
)
from backend.core.memory.in_memory_vector_store import (
    InMemoryVectorStore,
)
from backend.core.memory.memory_store import (
    MemoryStore,
)
from backend.core.memory.vector_memory import (
    VectorMemory,
)
from backend.core.memory.vector_store import (
    VectorStore,
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


def register_runtime_services(
    container: Container,
) -> None:
    """
    Register runtime-managed services.
    """

    # ------------------------------------------------------------------
    # Core application services
    # ------------------------------------------------------------------

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
        TaskService,
    ):
        container.register_singleton(
            TaskService,
        )

    if not container.contains(
        WorkflowService,
    ):
        container.register_singleton(
            WorkflowService,
        )

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

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

    if not container.contains(
        KernelLogger,
    ):
        container.register_singleton(
            KernelLogger,
        )

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    if not container.contains(
        ExecutionEngine,
    ):
        container.register_singleton(
            ExecutionEngine,
        )

    if not container.contains(
        ExecutionPipeline,
    ):
        container.register_singleton(
            ExecutionPipeline,
        )

    # ------------------------------------------------------------------
    # Memory
    #
    # VectorMemory is the production MemoryStore implementation: it
    # embeds every stored entry and answers queries via cosine
    # similarity search instead of substring matching. Embedding
    # generation and vector storage are both registered behind their
    # abstractions (EmbeddingProvider, VectorStore) so either can be
    # swapped for a real model/vector-database backend later without
    # touching VectorMemory or MemoryService.
    # ------------------------------------------------------------------

    if not container.contains(
        EmbeddingProvider,
    ):
        container.register_singleton(
            cast(
                type[Any],
                EmbeddingProvider,
            ),
            implementation=HashingEmbeddingProvider,
        )

    if not container.contains(
        EmbeddingService,
    ):
        container.register_singleton(
            EmbeddingService,
        )

    if not container.contains(
        VectorStore,
    ):
        container.register_singleton(
            cast(
                type[Any],
                VectorStore,
            ),
            implementation=InMemoryVectorStore,
        )

    if not container.contains(
        MemoryStore,
    ):
        container.register_singleton(
            cast(
                type[Any],
                MemoryStore,
            ),
            implementation=VectorMemory,
        )

    if not container.contains(
        MemoryService,
    ):
        container.register_singleton(
            MemoryService,
        )