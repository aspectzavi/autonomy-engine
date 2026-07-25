"""
Workflow builder.

Provides a fluent API for constructing workflows.

The builder is responsible for workflow construction only.
Execution remains the responsibility of WorkflowExecutor.
"""

from __future__ import annotations

from backend.core.tasks.task import Task
from backend.core.workflows.exceptions import (
    WorkflowDependencyError,
    WorkflowNodeError,
)
from backend.core.workflows.workflow import Workflow


class WorkflowBuilder:
    """
    Fluent workflow builder.
    """

    def __init__(
        self,
        *,
        name: str,
    ) -> None:
        self._workflow = Workflow(
            name=name,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def workflow(
        self,
    ) -> Workflow:
        """
        Underlying workflow.
        """
        return self._workflow

    # ------------------------------------------------------------------
    # Task Construction
    # ------------------------------------------------------------------

    def task(
        self,
        task: Task,
        *,
        id: str,
        name: str | None = None,
    ) -> WorkflowBuilder:
        """
        Add a task.

        Raises:
            WorkflowNodeError:
                If a duplicate node is added.
        """

        existing = {
            node.id
            for node in self.workflow.graph.nodes
        }

        if id in existing:
            raise WorkflowNodeError(
                f"Workflow node '{id}' already exists."
            )

        self.workflow.add_task(
            node_id=id,
            task=task,
            name=name,
        )

        return self

    # ------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------

    def after(
        self,
        dependency: str,
        task: str,
    ) -> WorkflowBuilder:
        """
        Register a dependency.

        Example

            builder.after(
                "search",
                "scrape",
            )

        Means:

            scrape depends on search.
        """

        nodes = {
            node.id
            for node in self.workflow.graph.nodes
        }

        if dependency not in nodes:
            raise WorkflowDependencyError(
                f"Unknown dependency '{dependency}'."
            )

        if task not in nodes:
            raise WorkflowDependencyError(
                f"Unknown task '{task}'."
            )

        self.workflow.depends_on(
            task_id=task,
            dependency_id=dependency,
        )

        return self

    def before(
        self,
        task: str,
        dependency: str,
    ) -> WorkflowBuilder:
        """
        Inverse of after().

        Example

            builder.before(
                "search",
                "scrape",
            )

        Means:

            search executes before scrape.
        """

        return self.after(
            task,
            dependency,
        )

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        validate: bool = True,
    ) -> Workflow:
        """
        Finalize the workflow.

        Validation is enabled by default.
        """

        if validate:
            self.workflow.validate()

        return self.workflow

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Builder diagnostics.
        """

        return {
            "workflow": self.workflow.diagnostics(),
        }