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
from backend.core.memory.memory_result import MemoryResult
from backend.core.observability.events import EventBus
from backend.core.runtime.execution_session import ExecutionSession


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
    # Retrieved memory relevant to the current goal.
    #
    memory: MemoryResult | None = None

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
        return self.variables.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.variables[key] = value

    def update(
        self,
        **variables: Any,
    ) -> None:
        self.variables.update(
            variables,
        )

    def contains(
        self,
        key: str,
    ) -> bool:
        return key in self.variables

    def clear(
        self,
    ) -> None:
        self.variables.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {
            "runtime_attached": (
                self.runtime is not None
            ),
            "session_attached": (
                self.session is not None
            ),
            "memory_attached": (
                self.memory is not None
            ),
            "variable_count": (
                len(self.variables)
            ),
            "metadata": self.metadata,
        }