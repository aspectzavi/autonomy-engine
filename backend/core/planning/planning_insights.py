"""
Planning insights.

Represents structured knowledge extracted from execution memory to
assist the planning subsystem.

The PlanningMemoryAnalyzer produces a PlanningInsights instance from
retrieved execution memories. Planners consume these insights without
depending on memory implementation details.

Future versions may include:

- successful execution strategies
- failed execution strategies
- preferred capabilities
- capability confidence scores
- execution ordering recommendations
- reusable workflow templates
- semantic similarity metrics
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class PlanningInsights:
    """
    Structured planning knowledge extracted from memory.
    """

    #
    # Basic execution history.
    #
    memory_count: int = 0

    has_history: bool = False

    #
    # Previously successful plans.
    #
    successful_plans: tuple[str, ...] = field(
        default_factory=tuple,
    )

    #
    # Previously failed plans.
    #
    failed_plans: tuple[str, ...] = field(
        default_factory=tuple,
    )

    #
    # Capabilities that have historically
    # performed well for similar goals.
    #
    suggested_capabilities: tuple[str, ...] = field(
        default_factory=tuple,
    )

    #
    # Optional planner recommendations.
    #
    recommended_order: tuple[str, ...] = field(
        default_factory=tuple,
    )

    #
    # Planner warnings extracted from history.
    #
    warnings: tuple[str, ...] = field(
        default_factory=tuple,
    )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def has_successful_history(
        self,
    ) -> bool:
        """
        Whether previous successful plans exist.
        """

        return bool(
            self.successful_plans,
        )

    @property
    def has_failed_history(
        self,
    ) -> bool:
        """
        Whether previous failed plans exist.
        """

        return bool(
            self.failed_plans,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether no planning knowledge exists.
        """

        return (
            self.memory_count == 0
            and not self.has_history
            and not self.successful_plans
            and not self.failed_plans
            and not self.suggested_capabilities
            and not self.recommended_order
            and not self.warnings
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return planning insight diagnostics.
        """

        return {
            "memory_count": self.memory_count,
            "has_history": self.has_history,
            "successful_plans": len(
                self.successful_plans,
            ),
            "failed_plans": len(
                self.failed_plans,
            ),
            "suggested_capabilities": len(
                self.suggested_capabilities,
            ),
            "recommended_order": len(
                self.recommended_order,
            ),
            "warnings": len(
                self.warnings,
            ),
        }