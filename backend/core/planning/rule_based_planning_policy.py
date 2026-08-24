"""
Rule-based planning policy.

Default deterministic implementation of the PlanningPolicy interface.

The policy interprets the ReasoningResult and constructs an appropriate
ExecutionPlan.

Capability selection is delegated to a CapabilitySelector while this
policy focuses solely on building an execution plan.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.capabilities.capability_registry import (
    CapabilityRegistry,
)
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)
from backend.core.planning.plan_step import (
    PlanStep,
)
from backend.core.planning.planning_insights import (
    PlanningInsights,
)
from backend.core.planning.planning_policy import (
    PlanningPolicy,
)
from backend.core.planning.registry_aware_capability_selector import (
    RegistryAwareCapabilitySelector,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class RuleBasedPlanningPolicy(
    PlanningPolicy,
):
    """
    Default deterministic planning policy.
    """

    #
    # The abstract placeholder capabilities this policy always knows
    # how to name/describe. Anything else is treated as a real,
    # registered capability (a tool), and gets the goal's metadata
    # passed through as its execution arguments.
    #
    _ABSTRACT_CAPABILITIES = frozenset(
        {
            "goal.execute",
            "goal.verify",
            "memory.search",
            "reasoning.analyze",
            "user.ask",
        },
    )

    def __init__(
        self,
        *,
        capability_registry: CapabilityRegistry | None = None,
    ) -> None:
        self._selector = (
            RegistryAwareCapabilitySelector(
                capability_registry=capability_registry,
            )
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def selector(
        self,
    ) -> RegistryAwareCapabilitySelector:
        """
        Capability selector.
        """

        return self._selector

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    async def build_plan(
        self,
        *,
        goal: Goal,
        context: AgentContext,
        reasoning: ReasoningResult,
        insights: PlanningInsights,
    ) -> ExecutionPlan:
        """
        Build an execution plan from a reasoning result.
        """

        selected = await self.selector.select(
            goal=goal,
            context=context,
            reasoning=reasoning,
            insights=insights,
        )

        steps = self._build_steps(
            goal=goal,
            capabilities=selected.capabilities,
        )

        return ExecutionPlan(
            name=goal.description,
            description=goal.description,
            steps=steps,
            metadata={
                "planning_policy": (
                    self.__class__.__name__
                ),
                "reasoning": {
                    "strategy": reasoning.strategy,
                    "decision": (
                        reasoning.decision.outcome
                    ),
                    "confidence": (
                        reasoning.confidence
                    ),
                },
                "memory": insights.diagnostics(),
                "capabilities": (
                    selected.diagnostics()
                ),
            },
        )

    # ------------------------------------------------------------------
    # Step construction
    # ------------------------------------------------------------------

    def _build_steps(
        self,
        *,
        goal: Goal,
        capabilities: tuple[str, ...],
    ) -> tuple[PlanStep, ...]:
        """
        Convert selected capabilities into plan steps.
        """

        if not capabilities:
            capabilities = (
                "goal.execute",
            )

        return tuple(
            self._step_for_capability(
                capability=capability,
                goal=goal,
                index=index,
            )
            for index, capability in enumerate(
                capabilities,
                start=1,
            )
        )

    def _step_for_capability(
        self,
        *,
        capability: str,
        goal: Goal,
        index: int,
    ) -> PlanStep:
        """
        Create a PlanStep for a capability.
        """

        names: dict[str, str] = {
            "goal.execute": "Execute goal",
            "goal.verify": "Verify result",
            "memory.search": "Search memory",
            "reasoning.analyze": "Analyze findings",
            "user.ask": "Request clarification",
        }

        descriptions: dict[str, str] = {
            "goal.execute": goal.description,
            "goal.verify": (
                "Verify successful completion."
            ),
            "memory.search": (
                "Retrieve relevant memories."
            ),
            "reasoning.analyze": (
                "Analyze gathered information."
            ),
            "user.ask": (
                "Obtain additional information "
                "before execution."
            ),
        }

        return PlanStep(
            id=f"step-{index}",
            name=names.get(
                capability,
                capability,
            ),
            description=descriptions.get(
                capability,
                goal.description,
            ),
            capability=capability,
            arguments=(
                dict(goal.metadata)
                if capability
                not in self._ABSTRACT_CAPABILITIES
                else {}
            ),
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "selector": (
                    self.selector.diagnostics()
                ),
                "type": "rule-based",
            }
        )

        return diagnostics