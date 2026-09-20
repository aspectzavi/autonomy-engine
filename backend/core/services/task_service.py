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
from backend.core.services.tool_service import ToolService
from backend.core.tasks.context import TaskContext
from backend.core.tasks.pipeline import TaskPipeline
from backend.core.tasks.queue import TaskQueue
from backend.core.tasks.result import TaskResult
from backend.core.tasks.rule_based_task_factory import (
    RuleBasedTaskFactory,
)
from backend.core.tasks.scheduler import TaskScheduler
from backend.core.tasks.task import Task
from backend.core.tasks.task_factory import TaskFactory


class TaskService(KernelService):
    """
    Runtime-managed task execution subsystem.
    """

    def __init__(
        self,
        *,
        pipeline: TaskPipeline | None = None,
        tool_service: ToolService | None = None,
        factory: TaskFactory | None = None,
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

        #
        # ToolService (not ToolManager) is injected here because
        # ToolService is what's actually registered as a container
        # singleton -- injecting ToolManager directly would get a
        # fresh, empty, disconnected manager rather than the one
        # holding the registered tools.
        #
        self._tool_service = tool_service

        #
        # tool_service (a registered singleton), not tool_manager
        # directly -- ToolManager itself isn't independently
        # registered in the container, so injecting it by type would
        # give this factory a disconnected, empty ToolManager instead
        # of the one ToolService actually populates in on_start().
        # Depending on the singleton service and reading `.manager`
        # off it keeps this pointed at the real, shared instance.
        #
        self._factory = (
            factory
            if factory is not None
            else RuleBasedTaskFactory(
                tool_manager=(
                    tool_service.manager
                    if tool_service is not None
                    else None
                ),
            )
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

    @property
    def factory(
        self,
    ) -> TaskFactory:
        """
        Return the task factory used by submit_capability().
        """

        return self._factory

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

    def create(
        self,
        *,
        capability: str,
        name: str | None = None,
    ) -> Task:
        """
        Create a task for a capability without queueing it.

        Resolves to a real ToolTask when `capability` matches a
        registered tool, otherwise a PlaceholderTask. See
        submit_capability() for the queueing counterpart.
        """

        return self._factory.create(
            capability=capability,
            name=name,
        )

    def submit_capability(
        self,
        capability: str,
        *,
        name: str | None = None,
    ) -> "TaskService":
        """
        Submit a task by capability name.

        Resolves to a real ToolTask when `capability` matches a
        registered tool (checked live -- this works correctly even
        if called before ToolService.on_start() has finished
        registering tools, as long as it's called after), otherwise
        falls back to a PlaceholderTask. This is the queue-based
        counterpart to how AgentService.execute() and
        RegistryAwareCapabilitySelector reach real tools -- the same
        capability name means the same tool either way.

        Returns:
            TaskService:
                Self, for fluent chaining.
        """

        return self.submit(
            self._factory.create(
                capability=capability,
                name=name,
            ),
        )

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
                "factory": (
                    self._factory.diagnostics()
                ),
            }
        )

        return diagnostics
