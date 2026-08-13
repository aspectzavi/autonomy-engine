"""
Agent execution context.

Provides the shared execution context available to an autonomous agent
during goal execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from backend.core.kernel.runtime_context import RuntimeContext
from backend.core.observability.events import EventBus
from backend.core.runtime.execution_memory import ExecutionMemory
from backend.core.runtime.execution_session import ExecutionSession
from backend.core.services.memory_service import (
    MemoryService,
)


@dataclass(slots=True)
class AgentContext:
    """
    Shared runtime context for autonomous agents.
    """

    #
    # Shared runtime infrastructure
    #
    event_bus: EventBus

    runtime: RuntimeContext | None = None

    session: ExecutionSession | None = None

    #
    # Runtime memory service.
    #
    memory_service: MemoryService | None = None

    #
    # Working execution memory.
    #
    memory: ExecutionMemory | None = None

    #
    # Arbitrary execution variables.
    #
    variables: dict[str, Any] = field(
        default_factory=dict,
    )

    #
    # Diagnostic metadata.
    #
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a runtime variable.
        """
        return self.variables.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a runtime variable.
        """
        self.variables[key] = value

    def update(
        self,
        **variables: Any,
    ) -> None:
        """
        Update multiple runtime variables.
        """
        self.variables.update(
            variables,
        )

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Whether a runtime variable exists.
        """
        return key in self.variables

    def clear(
        self,
    ) -> None:
        """
        Clear all runtime variables.
        """
        self.variables.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution context diagnostics.
        """
        return {
            "runtime_attached": (
                self.runtime is not None
            ),
            "session_attached": (
                self.session is not None
            ),
            "memory_service_attached": (
                self.memory_service is not None
            ),
            "memory_attached": (
                self.memory is not None
            ),
            "memory": (
                None
                if self.memory is None
                else self.memory.diagnostics()
            ),
            "variable_count": (
                len(self.variables)
            ),
            "metadata": self.metadata,
            
        }