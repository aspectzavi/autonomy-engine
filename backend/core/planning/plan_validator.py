"""
Plan validator.

Validates execution plans before they are transformed into workflows.

The planner is responsible for producing a plan.

The PlanValidator is responsible for ensuring that the produced plan is
structurally valid.

This separation allows planners to focus on reasoning while validation
remains deterministic.
"""

from __future__ import annotations

from backend.core.planning.execution_plan import ExecutionPlan
from backend.core.planning.plan_step import PlanStep


class PlanValidationError(ValueError):
    """
    Raised when an execution plan is invalid.
    """


class PlanValidator:
    """
    Validates execution plans.
    """

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Validate an execution plan.

        Raises:
            PlanValidationError:
                If the plan is invalid.
        """

        self._validate_name(
            plan,
        )

        self._validate_steps(
            plan,
        )

        self._validate_unique_ids(
            plan,
        )

        self._validate_dependencies(
            plan,
        )

    # ------------------------------------------------------------------
    # Internal Validation
    # ------------------------------------------------------------------

    def _validate_name(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Validate plan metadata.
        """

        if not plan.name.strip():
            raise PlanValidationError(
                "Execution plan must have a name."
            )

    def _validate_steps(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Validate that at least one step exists.
        """

        if plan.is_empty:
            raise PlanValidationError(
                "Execution plan contains no steps."
            )

    def _validate_unique_ids(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Validate unique step identifiers.
        """

        seen: set[str] = set()

        for step in plan.steps:
            if step.id in seen:
                raise PlanValidationError(
                    f"Duplicate step id '{step.id}'."
                )

            seen.add(
                step.id,
            )

    def _validate_dependencies(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Validate step dependencies.
        """

        step_ids = {
            step.id
            for step in plan.steps
        }

        for step in plan.steps:
            self._validate_step_dependencies(
                step,
                step_ids,
            )

    def _validate_step_dependencies(
        self,
        step: PlanStep,
        step_ids: set[str],
    ) -> None:
        """
        Validate dependencies for a single step.
        """

        if step.depends_on_step(
            step.id,
        ):
            raise PlanValidationError(
                f"Step '{step.id}' cannot depend on itself."
            )

        for dependency in step.depends_on:
            if dependency not in step_ids:
                raise PlanValidationError(
                    f"Unknown dependency "
                    f"'{dependency}' "
                    f"for step '{step.id}'."
                )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return validator diagnostics.
        """

        return {
            "validator": type(
                self,
            ).__name__,
        }