"""
Middleware context.

Represents the shared execution context flowing through the workflow
middleware pipeline.

The context is immutable except for the metadata dictionary, allowing
middleware to exchange execution information without mutating workflow
objects.

Future implementations may additionally include:

- authenticated principal
- cancellation tokens
- distributed trace identifiers
- execution deadlines
- resource budgets
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backend.core.tasks.context import (
    TaskContext,
)
from backend.core.workflows.workflow import (
    Workflow,
)


@dataclass(
    slots=True,
)
class MiddlewareContext:
    """
    Shared middleware execution context.
    """

    workflow: Workflow

    task_context: TaskContext

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store metadata.
        """

        self.metadata[key] = value

    def get(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve metadata.
        """

        return self.metadata.get(
            key,
            default,
        )

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Whether metadata exists.
        """

        return key in self.metadata

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware context diagnostics.
        """

        return {
            "workflow": self.workflow.name,
            "metadata_keys": tuple(
                sorted(
                    self.metadata.keys(),
                ),
            ),
            "metadata_count": len(
                self.metadata,
            ),
        }