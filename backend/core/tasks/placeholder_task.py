"""
Placeholder task.

Temporary executable task used until concrete capability-specific tasks
are implemented.

The PlaceholderTask allows the planning and workflow subsystems to be
developed independently from the concrete task implementations.

Future task factories will return specialized tasks instead of this
placeholder.
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.tasks.task import Task


class PlaceholderTask(Task):
    """
    Temporary executable task.

    Represents a capability that has not yet been implemented.
    """

    def __init__(
        self,
        *,
        capability: str,
        name: str,
    ) -> None:
        super().__init__(
            name=name,
        )
        self._capability = capability

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def capability(
        self,
    ) -> str:
        """
        Capability represented by this task.
        """

        return self._capability

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run(
        self,
        context: TaskContext,
    ) -> object:
        """
        Execute the placeholder task.

        This implementation intentionally performs no real work. It
        simply returns information describing the represented
        capability.
        """

        del context

        return {
            "status": "placeholder",
            "capability": self.capability,
            "message": (
                "No concrete task implementation is registered "
                "for this capability."
            ),
        }

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return task diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "capability": self.capability,
                "placeholder": True,
            },
        )

        return diagnostics