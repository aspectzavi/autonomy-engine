"""
Plan step.

Represents a single step within an execution plan.

Plan steps are produced by the planner and later translated into
workflow nodes by the WorkflowBuilder.

A PlanStep intentionally contains no runtime execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PlanStep:
    """
    Immutable execution plan step.
    """

    id: str

    name: str

    description: str

    capability: str

    depends_on: tuple[str, ...] = ()

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def has_dependencies(
        self,
    ) -> bool:
        """
        Whether this step depends on other steps.
        """

        return bool(
            self.depends_on,
        )

    @property
    def dependency_count(
        self,
    ) -> int:
        """
        Number of dependencies.
        """

        return len(
            self.depends_on,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def depends_on_step(
        self,
        step_id: str,
    ) -> bool:
        """
        Determine whether this step depends on another step.
        """

        return (
            step_id
            in self.depends_on
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return plan step diagnostics.
        """

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capability": self.capability,
            "dependency_count": self.dependency_count,
            "depends_on": self.depends_on,
            "metadata": self.metadata,
        }