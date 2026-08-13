"""
Rule-based workflow scheduler.

Default deterministic implementation.

Performs dependency-aware batching: nodes whose dependencies have all
been placed in an earlier group are grouped together so the runtime
can execute each group's nodes in parallel while still respecting the
workflow's dependency graph.

Future implementations may support:

- priority scheduling within a group
- distributed execution
- resource-aware group sizing
"""

from __future__ import annotations

from backend.core.workflows.scheduling_group import (
    SchedulingGroup,
)
from backend.core.workflows.scheduling_plan import (
    SchedulingPlan,
)
from backend.core.workflows.workflow import (
    Workflow,
)
from backend.core.workflows.workflow_scheduler import (
    WorkflowScheduler,
)


class RuleBasedWorkflowScheduler(
    WorkflowScheduler,
):
    """
    Default deterministic scheduler.
    """

    async def schedule(
        self,
        workflow: Workflow,
    ) -> SchedulingPlan:
        """
        Produce a dependency-aware scheduling plan.

        Nodes are grouped into successive "waves": a wave contains
        every node whose dependencies were all satisfied by nodes in
        earlier waves. Nodes within a wave carry no dependency on one
        another and are safe to execute in parallel.

        Raises:
            WorkflowCycleError:
                Propagated from graph validation if the workflow
                contains a cycle.
        """

        workflow.graph.validate()

        groups: list[SchedulingGroup] = []
        completed: set[str] = set()

        total_nodes = len(workflow.graph.nodes)

        while len(completed) < total_nodes:

            ready = workflow.graph.ready_nodes(
                completed,
            )

            group = SchedulingGroup(
                node_ids=tuple(
                    node.id for node in ready
                ),
            )

            groups.append(
                group,
            )

            completed.update(
                node.id for node in ready
            )

        return SchedulingPlan(
            groups=tuple(
                groups,
            ),
            metadata={
                "scheduler": (
                    self.__class__.__name__
                ),
                "strategy": (
                    "dependency_aware_batching"
                ),
                "waves": len(groups),
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "strategy": "dependency_aware_batching",
                "parallel_execution": True,
            },
        )

        return diagnostics