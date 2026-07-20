"""
Workflow graph.

Represents a directed acyclic graph (DAG) of workflow nodes.
"""

from __future__ import annotations

from collections import deque

from backend.core.workflows.edge import WorkflowEdge
from backend.core.workflows.node import WorkflowNode


class WorkflowGraph:
    """
    Directed acyclic workflow graph.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, WorkflowNode] = {}
        self._edges: set[WorkflowEdge] = set()

    # ------------------------------------------------------------------
    # Node Management
    # ------------------------------------------------------------------

    def add_node(
        self,
        node: WorkflowNode,
    ) -> None:
        """
        Add a node to the graph.
        """
        if node.id in self._nodes:
            raise ValueError(
                f"Node '{node.id}' already exists."
            )

        self._nodes[node.id] = node

    def remove_node(
        self,
        node_id: str,
    ) -> None:
        """
        Remove a node and its connected edges.
        """
        self._nodes.pop(node_id)

        self._edges = {
            edge
            for edge in self._edges
            if edge.source != node_id
            and edge.target != node_id
        }

        for node in self._nodes.values():
            node.remove_dependency(node_id)

    def node(
        self,
        node_id: str,
    ) -> WorkflowNode:
        """
        Retrieve a node.
        """
        return self._nodes[node_id]

    @property
    def nodes(self) -> tuple[WorkflowNode, ...]:
        """
        All workflow nodes.
        """
        return tuple(self._nodes.values())

    # ------------------------------------------------------------------
    # Edge Management
    # ------------------------------------------------------------------

    def add_edge(
        self,
        edge: WorkflowEdge,
    ) -> None:
        """
        Add a directed edge.
        """
        if edge.source not in self._nodes:
            raise KeyError(edge.source)

        if edge.target not in self._nodes:
            raise KeyError(edge.target)

        self._edges.add(edge)

        self._nodes[edge.target].add_dependency(
            edge.source
        )

    @property
    def edges(self) -> tuple[WorkflowEdge, ...]:
        """
        All workflow edges.
        """
        return tuple(self._edges)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def roots(self) -> tuple[WorkflowNode, ...]:
        """
        Nodes with no dependencies.
        """
        return tuple(
            node
            for node in self._nodes.values()
            if not node.depends_on
        )

    @property
    def leaves(self) -> tuple[WorkflowNode, ...]:
        """
        Nodes with no outgoing edges.
        """
        sources = {
            edge.source
            for edge in self._edges
        }

        return tuple(
            node
            for node in self._nodes.values()
            if node.id not in sources
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the graph.

        Raises:
            ValueError:
                If the graph contains a cycle.
        """
        self.topological_order()

    # ------------------------------------------------------------------
    # Topological Sort
    # ------------------------------------------------------------------

    def topological_order(
        self,
    ) -> tuple[WorkflowNode, ...]:
        """
        Return nodes in dependency order.

        Raises:
            ValueError:
                If the graph contains a cycle.
        """
        in_degree = {
            node.id: len(node.depends_on)
            for node in self._nodes.values()
        }

        queue = deque(
            node_id
            for node_id, degree in in_degree.items()
            if degree == 0
        )

        ordered: list[WorkflowNode] = []

        outgoing: dict[str, list[str]] = {}

        for edge in self._edges:
            outgoing.setdefault(
                edge.source,
                [],
            ).append(edge.target)

        while queue:
            current = queue.popleft()

            ordered.append(
                self._nodes[current]
            )

            for neighbour in outgoing.get(current, []):
                in_degree[neighbour] -= 1

                if in_degree[neighbour] == 0:
                    queue.append(neighbour)

        if len(ordered) != len(self._nodes):
            raise ValueError(
                "Workflow graph contains a cycle."
            )

        return tuple(ordered)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Graph diagnostics.
        """
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "roots": [
                node.id
                for node in self.roots
            ],
            "leaves": [
                node.id
                for node in self.leaves
            ],
        }