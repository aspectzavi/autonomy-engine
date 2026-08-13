"""
Tool execution context.

Provides the execution context supplied to tools.

ToolContext contains only tool-specific execution inputs. Runtime
services such as the dependency injection container, logger, runtime,
and event bus are owned by TaskContext.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolContext:
    """
    Context supplied to a tool during execution.
    """

    arguments: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    cancelled: bool = False

    # ------------------------------------------------------------------
    # Arguments
    # ------------------------------------------------------------------

    def argument(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Return a tool argument.
        """
        return self.arguments.get(
            name,
            default,
        )

    def has_argument(
        self,
        name: str,
    ) -> bool:
        """
        Whether the context contains an argument.
        """
        return name in self.arguments

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    def cancel(
        self,
    ) -> None:
        """
        Mark tool execution as cancelled.
        """
        self.cancelled = True

    @property
    def is_cancelled(
        self,
    ) -> bool:
        """
        Whether tool execution has been cancelled.
        """
        return self.cancelled

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return context diagnostics.
        """
        return {
            "arguments": tuple(
                self.arguments.keys()
            ),
            "metadata": self.metadata,
            "cancelled": self.cancelled,
        }