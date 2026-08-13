"""
Rule-based graph compiler.

Compiles an ExecutionGraph into an executable Workflow.

The compiler is responsible for:

- creating executable Tasks
- constructing workflow nodes
- wiring dependencies
- validating the workflow

The compiler performs no planning or optimization. Those stages have
already completed before compilation begins.
"""

from __future__ import annotations

from backend.core.planning.execution_graph import (
    ExecutionGraph,
)
from backend.core.tasks.task_factory import (
    TaskFactory,
)
from backend.core.workflows.graph_compiler import (
    GraphCompiler,
)
from backend.core.workflows.workflow import (
    Workflow,
)


class RuleBasedGraphCompiler(GraphCompiler):
    """
    Default deterministic graph compiler.
    """

    def __init__(
        self,
        *,
        task_factory: TaskFactory,
    ) -> None:
        self._task_factory = task_factory

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def task_factory(
        self,
    ) -> TaskFactory:
        """
        Task factory used during compilation.
        """

        return self._task_factory

    # ------------------------------------------------------------------
    # Compilation
    # ------------------------------------------------------------------

    async def compile(
        self,
        graph: ExecutionGraph,
    ) -> Workflow:
        """
        Compile an execution graph into a workflow.
        """

        workflow_name = graph.metadata.get(
            "name",
        )

        if not isinstance(
            workflow_name,
            str,
        ):
            workflow_name = "workflow"

        workflow = Workflow(
            name=workflow_name,
        )

        #
        # Create workflow tasks.
        #
        for step in graph.steps:
            task = self.task_factory.create(
                capability=step.capability,
                name=step.name,
            )

            workflow.add_task(
                step.id,
                task,
                name=step.name,
            )

        #
        # Register dependencies.
        #
        for source, target in graph.edges:
            workflow.depends_on(
                target,
                source,
            )

        workflow.validate()

        return workflow

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return compiler diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "task_factory": type(
                    self.task_factory,
                ).__name__,
                "task_factory_diagnostics": (
                    self.task_factory.diagnostics()
                ),
            },
        )

        return diagnostics