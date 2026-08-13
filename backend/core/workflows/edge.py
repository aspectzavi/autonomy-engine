"""
Workflow edge.

Represents a directed relationship between two workflow nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class WorkflowEdge:
    """
    Directed edge within a workflow graph.

    Represents:

        source ─────► target
    """

    source: str

    target: str

    label: str | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    def diagnostics(self) -> dict[str, object]:
        """
        Return edge diagnostics.
        """
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "metadata": self.metadata,
        }