"""
Optimization report.

Represents the immutable result produced by a PlanOptimizer.

The report summarizes every optimization applied to an execution plan
without modifying the plan itself.

Future optimizers may record:

- removed duplicate steps
- merged steps
- reordered steps
- inserted checkpoints
- inserted retries
- estimated execution cost
- estimated execution time
- estimated execution risk
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class OptimizationReport:
    """
    Immutable optimization report.
    """

    #
    # Whether the plan changed.
    #
    optimized: bool = False

    #
    # Human-readable optimization actions.
    #
    actions: tuple[str, ...] = field(
        default_factory=tuple,
    )

    #
    # Number of steps removed.
    #
    removed_steps: int = 0

    #
    # Number of steps inserted.
    #
    inserted_steps: int = 0

    #
    # Number of steps reordered.
    #
    reordered_steps: int = 0

    #
    # Estimated execution cost.
    #
    estimated_cost: float = 0.0

    #
    # Estimated execution time (seconds).
    #
    estimated_duration: float = 0.0

    #
    # Estimated execution risk.
    #
    estimated_risk: float = 0.0

    #
    # Additional optimizer metadata.
    #
    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def action_count(
        self,
    ) -> int:
        """
        Number of optimization actions.
        """

        return len(
            self.actions,
        )

    @property
    def has_actions(
        self,
    ) -> bool:
        """
        Whether any optimization actions were applied.
        """

        return self.action_count > 0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return optimization diagnostics.
        """

        return {
            "optimized": self.optimized,
            "actions": self.actions,
            "removed_steps": self.removed_steps,
            "inserted_steps": self.inserted_steps,
            "reordered_steps": self.reordered_steps,
            "estimated_cost": self.estimated_cost,
            "estimated_duration": self.estimated_duration,
            "estimated_risk": self.estimated_risk,
            "metadata": self.metadata,
        }