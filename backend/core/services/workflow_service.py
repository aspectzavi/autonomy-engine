"""
Workflow service.

Runtime-managed service responsible for coordinating workflow
execution throughout the autonomy engine.

The service is intentionally thin. It delegates orchestration to the
WorkflowRuntime, which coordinates scheduling and execution.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.observability.tracing import Tracing
from backend.core.tasks.context import TaskContext
from backend.core.workflows.default_workflow_monitor import (
    DefaultWorkflowMonitor,
)
from backend.core.workflows.default_workflow_recovery import (
    DefaultWorkflowRecovery,
)
from backend.core.workflows.default_workflow_resilience import (
    DefaultWorkflowResilience,
)
from backend.core.workflows.rule_based_failure_classifier import (
    RuleBasedFailureClassifier,
)
from backend.core.workflows.in_memory_checkpoint_store import (
    InMemoryCheckpointStore,
)
from backend.core.workflows.in_memory_workflow_event_bus import (
    InMemoryWorkflowEventBus,
)
from backend.core.workflows.rule_based_retry_policy import (
    RuleBasedRetryPolicy,
)
from backend.core.workflows.rule_based_workflow_executor import (
    RuleBasedWorkflowExecutor,
)
from backend.core.workflows.rule_based_workflow_scheduler import (
    RuleBasedWorkflowScheduler,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_runtime import (
    WorkflowRuntime,
)
from backend.core.workflows.workflow_runtime_pipeline import (
    WorkflowRuntimePipeline,
)


def _default_workflow_runtime() -> WorkflowRuntime:
    """
    Build a fully wired WorkflowRuntimePipeline with the same
    rule-based defaults the DI container uses.

    Used when WorkflowService is constructed standalone, outside the
    dependency injection container (e.g. in isolated tests that never
    call register_workflow_services). This exists so that path is
    never quietly weaker than the container-wired one — both produce
    the same monitored, resilient, event-emitting runtime.
    """

    classifier = RuleBasedFailureClassifier()

    return WorkflowRuntimePipeline(
        scheduler=RuleBasedWorkflowScheduler(),
        monitor=DefaultWorkflowMonitor(
            tracing=Tracing(),
        ),
        recovery=DefaultWorkflowRecovery(
            checkpoint_store=InMemoryCheckpointStore(),
        ),
        resilience=DefaultWorkflowResilience(
            executor=RuleBasedWorkflowExecutor(),
            retry_policy=RuleBasedRetryPolicy(
                classifier=classifier,
            ),
            failure_classifier=classifier,
        ),
        event_bus=InMemoryWorkflowEventBus(),
    )


class WorkflowService(KernelService):
    """
    Runtime service for workflow execution.
    """

    def __init__(
        self,
        *,
        workflow_runtime: WorkflowRuntime | None = None,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="workflow-service",
                version="1.0.0",
                description=(
                    "Coordinates execution of autonomous workflows."
                ),
            ),
        )

        self._workflow_runtime = (
            workflow_runtime
            or _default_workflow_runtime()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def workflow_runtime(
        self,
    ) -> WorkflowRuntime:
        """
        Workflow runtime.
        """

        return self._workflow_runtime

    # ------------------------------------------------------------------
    # Lifecycle Hooks
    # ------------------------------------------------------------------

    async def on_start(
        self,
    ) -> None:
        """
        Start workflow infrastructure.
        """

    async def on_stop(
        self,
    ) -> None:
        """
        Stop workflow infrastructure.
        """

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        workflow: Workflow,
        context: TaskContext,
    ) -> RuntimeReport:
        """
        Execute a workflow.
        """

        return await self.workflow_runtime.execute(
            workflow=workflow,
            context=context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return workflow service diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "workflow_runtime": (
                    self.workflow_runtime.diagnostics()
                ),
            }
        )

        return diagnostics