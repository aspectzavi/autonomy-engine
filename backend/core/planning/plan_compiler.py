"""
Plan compiler.

Compiles validated execution plans into executable workflows.

The compiler is responsible for translating planning-domain objects
into workflow-domain objects. It performs no planning and no execution.

Architecture:

Goal
    │
    ▼
Planner
    │
    ▼
ExecutionPlan
    │
    ▼
PlanValidator
    │
    ▼
PlanCompiler
    │
    ▼
CapabilityFactory
    │
    ▼
Workflow
"""

from __future__ import annotations

from backend.core.capabilities.capability_factory import (
    CapabilityFactory,
)
from backend.core.planning.execution_plan import ExecutionPlan
from backend.core.planning.plan_step import PlanStep
from backend.core.planning.plan_validator import PlanValidator
from backend.core.tasks.task import Task
from backend.core.workflows.workflow import Workflow


class PlanCompiler:
    """
    Compiles execution plans into workflows.
    """

    def __init__(
        self,
        *,
        capability_factory: CapabilityFactory,
        validator: PlanValidator | None = None,
    ) -> None:
        self._capability_factory = capability_factory
        self._validator = (
            validator
            or PlanValidator()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def capability_factory(
        self,
    ) -> CapabilityFactory:
        """
        Capability factory.
        """

        return self._capability_factory

    @property
    def validator(
        self,
    ) -> PlanValidator:
        """
        Plan validator.
        """

        return self._validator

    # ------------------------------------------------------------------
    # Compilation
    # ------------------------------------------------------------------

    def compile(
        self,
        plan: ExecutionPlan,
    ) -> Workflow:
        """
        Compile an execution plan into a workflow.
        """

        self.validator.validate(
            plan,
        )

        workflow = Workflow(
            name=plan.name,
        )

        #
        # Create workflow nodes.
        #
        for step in plan.steps:
            workflow.add_task(
                node_id=step.id,
                task=self._create_task(
                    step,
                ),
                name=step.name,
            )

        #
        # Create workflow edges.
        #
        for step in plan.steps:
            for dependency in step.depends_on:
                workflow.depends_on(
                    task_id=step.id,
                    dependency_id=dependency,
                )

        workflow.validate()

        return workflow

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _create_task(
        self,
        step: PlanStep,
    ) -> Task:
        """
        Convert a plan step into an executable workflow task.
        """

        return self.capability_factory.create(
            capability=step.capability,
            task_name=step.name,
            arguments=step.arguments,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Compiler diagnostics.
        """

        return {
            "validator": (
                self.validator.__class__.__name__
            ),
            "capability_factory": (
                self.capability_factory.__class__.__name__
            ),
        }