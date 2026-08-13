"""
Workflow.

High-level abstraction representing an executable workflow.
"""

from __future__ import annotations

from backend.core.tasks.task import Task
from backend.core.workflows.edge import WorkflowEdge
from backend.core.workflows.graph import WorkflowGraph
from backend.core.workflows.node import WorkflowNode
from backend.core.workflows.state import WorkflowState


class Workflow:
    """
    Executable workflow.

    Owns workflow lifecycle and graph construction.
    """

    def __init__(
        self,
        *,
        name: str,
    ) -> None:
        self._name = name
        self._graph = WorkflowGraph()
        self._state = WorkflowState.CREATED

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Workflow name.
        """
        return self._name

    @property
    def graph(self) -> WorkflowGraph:
        """
        Workflow graph.
        """
        return self._graph

    @property
    def state(self) -> WorkflowState:
        """
        Current workflow state.
        """
        return self._state

    # ------------------------------------------------------------------
    # Graph Construction
    # ------------------------------------------------------------------

    def add_task(
        self,
        node_id: str,
        task: Task,
        *,
        name: str | None = None,
    ) -> WorkflowNode:
        """
        Add a task to the workflow.
        """
        node = WorkflowNode(
            id=node_id,
            task=task,
            name=name,
        )

        self.graph.add_node(node)

        return node

    def depends_on(
        self,
        task_id: str,
        dependency_id: str,
    ) -> None:
        """
        Register a dependency.

        task_id depends on dependency_id.
        """
        self.graph.add_edge(
            WorkflowEdge(
                source=dependency_id,
                target=task_id,
            )
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the workflow.
        """
        self._state = WorkflowState.VALIDATING

        self.graph.validate()

        self._state = WorkflowState.READY

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Workflow diagnostics.
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "graph": self.graph.diagnostics(),
        }