"""
Workflow scheduler.

Determines the order in which workflow nodes become eligible for
execution.

The scheduler is intentionally independent of task execution. It only
tracks workflow progress and identifies runnable nodes.
"""

from __future__ import annotations

from collections import deque

from backend.core.workflows.node import WorkflowNode
from backend.core.workflows.workflow import Workflow


class WorkflowScheduler:
    """
    Workflow scheduler.

    Maintains execution state for a workflow and exposes the set of
    nodes that are currently ready for execution.
    """

    def __init__(
        self,
        workflow: Workflow,
    ) -> None:
        self._workflow = workflow

        #
        # Completed nodes.
        #
        self._completed: set[str] = set()

        #
        # Nodes already scheduled.
        #
        self._scheduled: set[str] = set()

        #
        # Ready queue.
        #
        self._ready: deque[WorkflowNode] = deque()

        self._initialize()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def workflow(
        self,
    ) -> Workflow:
        """
        Workflow being scheduled.
        """
        return self._workflow

    @property
    def completed(
        self,
    ) -> frozenset[str]:
        """
        Completed node ids.
        """
        return frozenset(
            self._completed,
        )

    @property
    def scheduled(
        self,
    ) -> frozenset[str]:
        """
        Already scheduled node ids.
        """
        return frozenset(
            self._scheduled,
        )

    @property
    def finished(
        self,
    ) -> bool:
        """
        True when every workflow node has completed.
        """
        return (
            len(self._completed)
            == len(self.workflow.graph.nodes)
        )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(
        self,
    ) -> None:
        """
        Seed the ready queue using workflow roots.
        """

        for node in self.workflow.graph.roots:
            self._ready.append(
                node,
            )
            self._scheduled.add(
                node.id,
            )

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def has_ready(
        self,
    ) -> bool:
        """
        Whether runnable nodes exist.
        """
        return bool(
            self._ready,
        )

    def next_node(
        self,
    ) -> WorkflowNode:
        """
        Return the next runnable node.

        Raises:
            IndexError:
                If no nodes are ready.
        """

        return self._ready.popleft()

    def complete(
        self,
        node_id: str,
    ) -> None:
        """
        Mark a node as completed and schedule any newly
        available nodes.
        """

        if node_id in self._completed:
            return

        self._completed.add(
            node_id,
        )

        for node in self.workflow.graph.nodes:

            if node.id in self._scheduled:
                continue

            if all(
                dependency in self._completed
                for dependency in node.depends_on
            ):
                self._ready.append(
                    node,
                )

                self._scheduled.add(
                    node.id,
                )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def runnable(
        self,
    ) -> tuple[WorkflowNode, ...]:
        """
        Snapshot of currently runnable nodes.
        """

        return tuple(
            self._ready,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Scheduler diagnostics.
        """

        return {
            "workflow": self.workflow.name,
            "ready": [
                node.id
                for node in self._ready
            ],
            "completed": sorted(
                self._completed,
            ),
            "scheduled": sorted(
                self._scheduled,
            ),
            "finished": self.finished,
        }