"""
Task service.

Runtime-managed service responsible for the task execution subsystem.

The service is intentionally thin. It delegates queueing and
execution to TaskPipeline (queue + scheduler + executor), the same
way WorkflowService delegates to WorkflowRuntime and ToolService
delegates to ToolManager.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.tasks.context import TaskContext
from backend.core.tasks.pipeline import TaskPipeline
from backend.core.tasks.queue import TaskQueue
from backend.core.tasks.result import TaskResult
from backend.core.tasks.scheduler import TaskScheduler
from backend.core.tasks.task import Task


class TaskService(KernelService):
    """
    Runtime-managed task execution subsystem.
    """

    def __init__(
        self,
        *,
        pipeline: TaskPipeline | None = None,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="task-service",
                version="1.0.0",
                description=(
                    "Runtime-managed task execution subsystem."
                ),
            ),
        )

        #
        # NOTE: `is None`, not `pipeline or TaskPipeline()`.
        # See the __len__ falsy-empty-collection bug fixed in
        # AgentManager, ToolManager, and TaskScheduler -- the same
        # discipline applies to every optional DI-injected dependency
        # here, even ones that are currently safe, to keep this class
        # consistent with the rest of the codebase.
        #
        self._pipeline = (
            pipeline
            if pipeline is not None
            else TaskPipeline()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def pipeline(
        self,
    ) -> TaskPipeline:
        """
        Return the managed task pipeline.
        """

        return self._pipeline

    @property
    def scheduler(
        self,
    ) -> TaskScheduler:
        """
        Return the task scheduler.
        """

        return self.pipeline.scheduler

    @property
    def queue(
        self,
    ) -> TaskQueue:
        """
        Return the task queue.
        """

        return self.scheduler.queue

    # ------------------------------------------------------------------
    # Submission
    # ------------------------------------------------------------------

    def submit(
        self,
        task: Task,
    ) -> "TaskService":
        """
        Submit a task for execution.

        Returns:
            TaskService:
                Self, for fluent chaining.
        """

        self.pipeline.add(
            task,
        )

        return self

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run_next(
        self,
        context: TaskContext,
    ) -> TaskResult:
        """
        Execute the next queued task.

        Raises:
            IndexError:
                If the queue is empty.
        """

        return await self.scheduler.run_next(
            context,
        )

    async def run_all(
        self,
        context: TaskContext,
    ) -> list[TaskResult]:
        """
        Execute every queued task.
        """

        return await self.pipeline.run(
            context,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def on_start(
        self,
    ) -> None:
        """
        Start the task subsystem.
        """

        self.logger.info(
            "Task subsystem started with %d queued task(s).",
            len(self.queue),
        )

    async def on_stop(
        self,
    ) -> None:
        """
        Stop the task subsystem.
        """

        self.pipeline.clear()

        self.logger.info(
            "Task queue cleared.",
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return task service diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "pipeline": (
                    self.pipeline.diagnostics()
                ),
            }
        )

        return diagnostics
