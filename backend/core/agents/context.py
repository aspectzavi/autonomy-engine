"""
Agent execution context.

Provides the runtime context available to an autonomous agent while
working toward a goal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.observability.events import EventBus


@dataclass(slots=True)
class AgentContext:
    """
    Runtime context shared across agent execution.

    The context carries shared services and arbitrary execution data
    throughout the agent lifecycle.
    """

    event_bus: EventBus = field(
        default_factory=EventBus,
    )

    variables: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a context variable.
        """
        return self.variables.get(key, default)

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a context variable.
        """
        self.variables[key] = value

    def update(
        self,
        **variables: Any,
    ) -> None:
        """
        Update multiple variables.
        """
        self.variables.update(variables)

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Whether a variable exists.
        """
        return key in self.variables

    def clear(self) -> None:
        """
        Remove all runtime variables.
        """
        self.variables.clear()

    def diagnostics(self) -> dict[str, object]:
        """
        Return context diagnostics.
        """
        return {
            "variable_count": len(self.variables),
            "metadata": self.metadata,
        }