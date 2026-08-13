"""
Rule-based plan optimizer.

Default implementation of the PlanOptimizer interface.

This optimizer performs lightweight deterministic optimizations before
an ExecutionPlan is compiled into a workflow.

Current optimizations:

- remove duplicate capabilities
- preserve execution order
- estimate execution cost
- estimate execution duration
- estimate execution risk

Future versions may introduce:

- dependency analysis
- step reordering
- checkpoint insertion
- retry insertion
- parallel execution grouping
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)
from backend.core.planning.optimization_report import (
    OptimizationReport,
)
from backend.core.planning.plan_optimizer import (
    PlanOptimizer,
)
from backend.core.planning.plan_step import (
    PlanStep,
)


class RuleBasedPlanOptimizer(
    PlanOptimizer,
):
    """
    Default deterministic plan optimizer.
    """

    async def optimize(
        self,
        *,
        plan: ExecutionPlan,
        context: AgentContext,
    ) -> tuple[
        ExecutionPlan,
        OptimizationReport,
    ]:
        """
        Optimize an execution plan.
        """

        #
        # Reserved for future optimizations.
        #
        del context

        seen: set[str] = set()

        optimized_steps: list[PlanStep] = []

        removed = 0

        actions: list[str] = []

        for step in plan.steps:
            if step.capability in seen:
                removed += 1
                continue

            seen.add(
                step.capability,
            )

            optimized_steps.append(
                step,
            )

        if removed:
            actions.append(
                f"Removed {removed} duplicate step(s)."
            )

        optimized_plan = ExecutionPlan(
            name=plan.name,
            description=plan.description,
            steps=tuple(
                optimized_steps,
            ),
            created_at=plan.created_at,
            metadata={
                **plan.metadata,
                "optimized": True,
            },
        )

        report = OptimizationReport(
            optimized=removed > 0,
            actions=tuple(
                actions,
            ),
            removed_steps=removed,
            inserted_steps=0,
            reordered_steps=0,
            estimated_cost=self._estimate_cost(
                optimized_plan,
            ),
            estimated_duration=self._estimate_duration(
                optimized_plan,
            ),
            estimated_risk=self._estimate_risk(
                optimized_plan,
            ),
            metadata={
                "optimizer": (
                    self.__class__.__name__
                ),
            },
        )

        return (
            optimized_plan,
            report,
        )

    # ------------------------------------------------------------------
    # Estimation
    # ------------------------------------------------------------------

    def _estimate_cost(
        self,
        plan: ExecutionPlan,
    ) -> float:
        """
        Estimate execution cost.

        Current implementation assigns a unit cost per step.
        """

        return float(
            plan.step_count,
        )

    def _estimate_duration(
        self,
        plan: ExecutionPlan,
    ) -> float:
        """
        Estimate execution duration in seconds.
        """

        return (
            float(
                plan.step_count,
            )
            * 2.0
        )

    def _estimate_risk(
        self,
        plan: ExecutionPlan,
    ) -> float:
        """
        Estimate execution risk.

        Current implementation scales risk with plan size and clamps
        the value between 0.0 and 1.0.
        """

        risk = (
            plan.step_count * 0.1
        )

        return min(
            risk,
            1.0,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return optimizer diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "type": "rule-based",
                "optimizations": (
                    "duplicate-removal",
                    "cost-estimation",
                    "duration-estimation",
                    "risk-estimation",
                ),
            }
        )

        return diagnostics