
"""
Workflow runtime pipeline.

Coordinates the complete workflow runtime lifecycle.

The pipeline is intentionally orchestration-only. It delegates
execution, monitoring, recovery, and resilience behavior to their
dedicated components.

Execution flow:

    Workflow
        │
        ▼
    Validation
        │
        ▼
    Scheduler
        │
        ▼
    SchedulingPlan
        │
        ▼
    Monitor.begin()
        │
        ▼
    Resilience
        │
        ├── Retry Policy
        ├── Failure Classification
        └── Executor
        │
        ▼
    ExecutionResult
        │
        ├── Monitor.finish()
        ├── Recovery
        └── Event Bus
        │
        ▼
    RuntimeReport
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.workflows.runtime_report import RuntimeReport
from backend.core.workflows.scheduling_plan import SchedulingPlan
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_event import WorkflowEvent
from backend.core.workflows.workflow_event_bus import WorkflowEventBus
from backend.core.workflows.workflow_execution_context import (
    WorkflowExecutionContext,
)
from backend.core.workflows.workflow_monitor import WorkflowMonitor
from backend.core.workflows.workflow_recovery import WorkflowRecovery
from backend.core.workflows.workflow_resilience import (
    WorkflowResilience,
)
from backend.core.workflows.workflow_scheduler import WorkflowScheduler


__all__ = [
    "WorkflowRuntimePipeline",
]


class WorkflowRuntimePipeline:
    """
    Coordinates workflow runtime execution.

    This class contains orchestration logic only. It does not perform
    scheduling, execution, retry, failure classification, monitoring,
    recovery, or resilience logic itself.
    """

    def __init__(
        self,
        *,
        scheduler: WorkflowScheduler,
        monitor: WorkflowMonitor,
        recovery: WorkflowRecovery,
        resilience: WorkflowResilience,
        event_bus: WorkflowEventBus,
    ) -> None:
        self._scheduler = scheduler
        self._monitor = monitor
        self._recovery = recovery
        self._resilience = resilience
        self._event_bus = event_bus

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def scheduler(
        self,
    ) -> WorkflowScheduler:
        """
        Workflow scheduler.
        """
        return self._scheduler

    @property
    def monitor(
        self,
    ) -> WorkflowMonitor:
        """
        Workflow monitor.
        """
        return self._monitor

    @property
    def recovery(
        self,
    ) -> WorkflowRecovery:
        """
        Workflow recovery component.
        """
        return self._recovery

    @property
    def resilience(
        self,
    ) -> WorkflowResilience:
        """
        Workflow resilience component.
        """
        return self._resilience

    @property
    def event_bus(
        self,
    ) -> WorkflowEventBus:
        """
        Workflow event bus.
        """
        return self._event_bus

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        *,
        workflow: Workflow,
        context: TaskContext,
    ) -> RuntimeReport:
        """
        Execute the complete workflow lifecycle.
        """

        # --------------------------------------------------------------
        # Validation
        # --------------------------------------------------------------

        workflow.validate()

        runtime = WorkflowExecutionContext(
            workflow=workflow,
            task_context=context,
        )

        # --------------------------------------------------------------
        # Workflow started
        # --------------------------------------------------------------

        runtime.publish(
            "workflow.started",
        )

        await self.event_bus.publish(
            WorkflowEvent(
                name="workflow.started",
                workflow=workflow.name,
            ),
        )

        # --------------------------------------------------------------
        # Scheduling
        # --------------------------------------------------------------

        schedule: SchedulingPlan = (
            await self.scheduler.schedule(
                workflow,
            )
        )

        runtime.put_state(
            "schedule",
            schedule,
        )

        runtime.publish(
            "workflow.scheduled",
        )

        await self.event_bus.publish(
            WorkflowEvent(
                name="workflow.scheduled",
                workflow=workflow.name,
            ),
        )

        # --------------------------------------------------------------
        # Monitoring begins before execution
        # --------------------------------------------------------------

        await self.monitor.begin(
            workflow=workflow,
        )

        runtime.publish(
            "workflow.monitoring.started",
        )

        # --------------------------------------------------------------
        # Resilient execution
        # --------------------------------------------------------------

        execution, resilience_report = (
            await self.resilience.execute(
                workflow=workflow,
                schedule=schedule,
                context=context,
            )
        )

        runtime.put_state(
            "execution",
            execution,
        )

        runtime.put_state(
            "resilience",
            resilience_report,
        )

        runtime.publish(
            "workflow.executed",
        )

        # --------------------------------------------------------------
        # Monitoring finishes after execution
        # --------------------------------------------------------------

        await self.monitor.finish(
            workflow=workflow,
            result=execution,
        )

        metrics = self.monitor.metrics()
        trace = self.monitor.trace()

        runtime.put_state(
            "metrics",
            metrics,
        )

        runtime.put_state(
            "trace",
            trace,
        )

        runtime.publish(
            "workflow.monitoring.finished",
        )

        # --------------------------------------------------------------
        # Recovery
        # --------------------------------------------------------------

        recovery_report = await self.recovery.recover(
            workflow=workflow,
            context=context,
        )

        runtime.put_state(
            "recovery",
            recovery_report,
        )

        runtime.publish(
            "workflow.recovery.completed",
        )

        # --------------------------------------------------------------
        # Workflow finished
        # --------------------------------------------------------------

        await self.event_bus.publish(
            WorkflowEvent(
                name="workflow.finished",
                workflow=workflow.name,
            ),
        )

        runtime.publish(
            "workflow.finished",
        )

        # --------------------------------------------------------------
        # Runtime report
        # --------------------------------------------------------------

        return RuntimeReport(
            schedule=schedule,
            execution=execution,
            metadata={
                "runtime": type(self).__name__,
                "events": tuple(
                    runtime.events,
                ),
                "runtime_context": runtime.diagnostics(),
                "resilience": resilience_report,
                "recovery": recovery_report,
                "metrics": metrics,
                "trace": trace,
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return pipeline diagnostics.
        """

        return {
            "pipeline": type(self).__name__,
            "scheduler": type(
                self.scheduler,
            ).__name__,
            "monitor": type(
                self.monitor,
            ).__name__,
            "recovery": type(
                self.recovery,
            ).__name__,
            "resilience": type(
                self.resilience,
            ).__name__,
            "event_bus": type(
                self.event_bus,
            ).__name__,
        }
