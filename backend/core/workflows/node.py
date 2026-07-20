"""
Workflow node.

Represents a single node within a workflow graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.core.tasks.task import Task


@dataclass(slots=True)
class WorkflowNode:
    """
    A node in a workflow graph.

    Wraps a Task with workflow-specific metadata.
    """

    id: str

    task: Task

    name: str | None = None

    depends_on: set[str] = field(
        default_factory=set,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    @property
    def display_name(self) -> str:
        """
        Human-readable node name.
        """
        return self.name or self.task.name

    def add_dependency(
        self,
        node_id: str,
    ) -> None:
        """
        Add a dependency.
        """
        self.depends_on.add(node_id)

    def remove_dependency(
        self,
        node_id: str,
    ) -> None:
        """
        Remove a dependency.
        """
        self.depends_on.discard(node_id)

    @property
    def dependency_count(self) -> int:
        """
        Number of dependencies.
        """
        return len(self.depends_on)

    def diagnostics(self) -> dict[str, object]:
        """
        Return diagnostics for this node.
        """
        return {
            "id": self.id,
            "name": self.display_name,
            "task": self.task.name,
            "status": self.task.status.value,
            "dependencies": sorted(self.depends_on),
            "metadata": self.metadata,
        }