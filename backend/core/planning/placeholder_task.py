"""
Placeholder task.

Temporary task implementation used while compiling execution plans into
workflows.

This task will later be replaced by capability-specific task factories.
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.tasks.task import Task


class PlaceholderTask(Task):
    """
    Temporary executable task.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
        capability: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            name=name,
        )

        self._description = description
        self._capability = capability
        self._metadata = metadata or {}

    @property
    def description(
        self,
    ) -> str:
        return self._description

    @property
    def capability(
        self,
    ) -> str:
        return self._capability

    @property
    def metadata(
        self,
    ) -> dict[str, object]:
        return self._metadata

    async def run(
        self,
        context: TaskContext,
    ) -> object:
        """
        Placeholder execution.

        Future versions will be replaced by real capability-specific
        implementations.
        """

        return {
            "status": "placeholder",
            "task": self.name,
            "capability": self.capability,
        }

    def diagnostics(
        self,
    ) -> dict[str, object]:
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "description": self.description,
                "capability": self.capability,
                "metadata": self.metadata,
            },
        )

        return diagnostics