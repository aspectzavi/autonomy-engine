"""
Workflow runtime pipeline tests.

Tests the orchestration contract of WorkflowRuntimePipeline.

The pipeline coordinates the workflow lifecycle while delegating
business behavior to its injected components.
"""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from backend.app.container.container import Container
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext
from backend.core.workflows.execution_result import ExecutionResult
from backend.core.workflows.recovery_report import RecoveryReport
from backend.core.workflows.resilience_report import ResilienceReport
from backend.core.workflows.runtime_report import RuntimeReport
from backend.core.workflows.scheduling_plan import SchedulingPlan
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_event import WorkflowEvent
from backend.core.workflows.workflow_event_bus import WorkflowEventBus
from backend.core.workflows.workflow_event_listener import (
    WorkflowEventListener,
)
from backend.core.workflows.workflow_execution_context import (
    WorkflowExecutionContext,
)
from backend.core.workflows.workflow_metrics import WorkflowMetrics
from backend.core.workflows.workflow_monitor import WorkflowMonitor
from backend.core.workflows.workflow_recovery import WorkflowRecovery
from backend.core.workflows.workflow_resilience import (
    WorkflowResilience,
)
from backend.core.workflows.workflow_runtime_pipeline import (
    WorkflowRuntimePipeline,
)
from backend.core.workflows.workflow_scheduler import WorkflowScheduler
from backend.core.workflows.workflow_trace import WorkflowTrace

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def create_workflow() -> Workflow:
    """Create a minimal valid workflow."""
    return Workflow(
        name="pipeline-test-workflow",
    )

def create_task_context() -> TaskContext:
    """Create a task context compatible with the current runtime contract."""
    return TaskContext(
        runtime=Mock(),
        container=Container(),
        logger=KernelLogger(),
        events=EventBus(),
    )

def create_schedule() -> SchedulingPlan:
    """
    Create an opaque scheduling plan.

    The pipeline passes the scheduling plan between the scheduler and
    resilience component without inspecting its internal structure.
    """
    return cast(
        SchedulingPlan,
        Mock(spec=SchedulingPlan),
    )

def create_execution_result() -> ExecutionResult:
    """
    Create an opaque execution result.

    The pipeline passes this object between components without depending
    on implementation-specific fields.
    """
    return cast(
        ExecutionResult,
        Mock(spec=ExecutionResult),
    )

def create_metrics() -> WorkflowMetrics:
    """Create an opaque metrics object."""
    return cast(
        WorkflowMetrics,
        Mock(spec=WorkflowMetrics),
    )

def create_trace() -> WorkflowTrace:
    """Create an opaque trace object."""
    return cast(
        WorkflowTrace,
        Mock(spec=WorkflowTrace),
    )

def create_recovery_report() -> RecoveryReport:
    """
    Create a recovery report using the current report contract.
    """
    return cast(
        RecoveryReport,
        Mock(spec=RecoveryReport),
    )

def create_resilience_report() -> ResilienceReport:
    """Create a resilience report using the current contract."""
    return ResilienceReport(
        successful=True,
    )

# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------

class RecordingScheduler(WorkflowScheduler):
    """Scheduler test double."""

    def __init__(
        self,
        schedule: SchedulingPlan,
        calls: list[str],
    ) -> None:
        self.schedule_result = schedule
        self.calls = calls
        self.workflow: Workflow | None = None

    async def schedule(
        self,
        workflow: Workflow,
    ) -> SchedulingPlan:
        self.calls.append(
            "scheduler",
        )

        self.workflow = workflow

        return self.schedule_result

class RecordingMonitor(WorkflowMonitor):
    """Monitor test double."""

    def __init__(
        self,
        calls: list[str],
        metrics: WorkflowMetrics,
        trace: WorkflowTrace,
    ) -> None:
        self.calls = calls
        self.metrics_result = metrics
        self.trace_result = trace

        self.begin_workflow: Workflow | None = None
        self.finish_workflow: Workflow | None = None
        self.finish_result: ExecutionResult | None = None

    async def begin(
        self,
        *,
        workflow: Workflow,
    ) -> None:
        self.calls.append(
            "monitor.begin",
        )

        self.begin_workflow = workflow

    async def finish(
        self,
        *,
        workflow: Workflow,
        result: ExecutionResult,
    ) -> None:
        self.calls.append(
            "monitor.finish",
        )

        self.finish_workflow = workflow
        self.finish_result = result

    def metrics(
        self,
    ) -> WorkflowMetrics:
        return self.metrics_result

    def trace(
        self,
    ) -> WorkflowTrace:
        return self.trace_result

class RecordingRecovery(WorkflowRecovery):
    """Recovery test double."""

    def __init__(
        self,
        report: RecoveryReport,
        calls: list[str],
    ) -> None:
        self.report = report
        self.calls = calls

        self.workflow: Workflow | None = None
        self.context: TaskContext | None = None

    async def recover(
        self,
        *,
        workflow: Workflow,
        context: TaskContext,
    ) -> RecoveryReport:
        self.calls.append(
            "recovery",
        )

        self.workflow = workflow
        self.context = context

        return self.report

class RecordingResilience(WorkflowResilience):
    """Resilience test double."""

    def __init__(
        self,
        execution: ExecutionResult,
        report: ResilienceReport,
        calls: list[str],
    ) -> None:
        self.execution_result = execution
        self.report = report
        self.calls = calls

        self.workflow: Workflow | None = None
        self.schedule: SchedulingPlan | None = None
        self.context: TaskContext | None = None

    async def execute(
        self,
        *,
        workflow: Workflow,
        schedule: SchedulingPlan,
        context: TaskContext,
    ) -> tuple[
        ExecutionResult,
        ResilienceReport,
    ]:
        self.calls.append(
            "resilience",
        )

        self.workflow = workflow
        self.schedule = schedule
        self.context = context

        return (
            self.execution_result,
            self.report,
        )

class RecordingEventBus(WorkflowEventBus):
    """
    Complete event-bus test double.

    All abstract members are implemented according to the current
    WorkflowEventBus contract.
    """

    def __init__(
        self,
        calls: list[str],
    ) -> None:
        self.calls = calls
        self.events: list[WorkflowEvent] = []
        self._listeners: list[WorkflowEventListener] = []

    async def publish(
        self,
        event: WorkflowEvent,
    ) -> None:
        self.events.append(
            event,
        )

        self.calls.append(
            f"event:{event.name}",
        )

    async def subscribe(
        self,
        listener: WorkflowEventListener,
    ) -> None:
        if listener not in self._listeners:
            self._listeners.append(
                listener,
            )

    async def unsubscribe(
        self,
        listener: WorkflowEventListener,
    ) -> None:
        if listener in self._listeners:
            self._listeners.remove(
                listener,
            )

    def listeners(
        self,
    ) -> tuple[
        WorkflowEventListener,
        ...,
    ]:
        return tuple(
            self._listeners,
        )

# ---------------------------------------------------------------------------
# Pipeline factory
# ---------------------------------------------------------------------------

def create_pipeline(
    calls: list[str] | None = None,
) -> tuple[
    WorkflowRuntimePipeline,
    RecordingScheduler,
    RecordingMonitor,
    RecordingRecovery,
    RecordingResilience,
    RecordingEventBus,
    SchedulingPlan,
    ExecutionResult,
    WorkflowMetrics,
    WorkflowTrace,
    RecoveryReport,
    ResilienceReport,
]:
    """Create a fully isolated workflow runtime pipeline."""

    if calls is None:
        calls = []

    schedule = create_schedule()
    execution = create_execution_result()
    metrics = create_metrics()
    trace = create_trace()
    recovery_report = create_recovery_report()
    resilience_report = create_resilience_report()

    scheduler = RecordingScheduler(
        schedule=schedule,
        calls=calls,
    )

    monitor = RecordingMonitor(
        calls=calls,
        metrics=metrics,
        trace=trace,
    )

    recovery = RecordingRecovery(
        report=recovery_report,
        calls=calls,
    )

    resilience = RecordingResilience(
        execution=execution,
        report=resilience_report,
        calls=calls,
    )

    event_bus = RecordingEventBus(
        calls=calls,
    )

    pipeline = WorkflowRuntimePipeline(
        scheduler=scheduler,
        monitor=monitor,
        recovery=recovery,
        resilience=resilience,
        event_bus=event_bus,
    )

    return (
        pipeline,
        scheduler,
        monitor,
        recovery,
        resilience,
        event_bus,
        schedule,
        execution,
        metrics,
        trace,
        recovery_report,
        resilience_report,
    )

# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def test_pipeline_exposes_scheduler() -> None:
    pipeline, scheduler, *_ = create_pipeline()

    assert pipeline.scheduler is scheduler

def test_pipeline_exposes_monitor() -> None:
    pipeline, _, monitor, *_ = create_pipeline()

    assert pipeline.monitor is monitor

def test_pipeline_exposes_recovery() -> None:
    pipeline, _, _, recovery, *_ = create_pipeline()

    assert pipeline.recovery is recovery

def test_pipeline_exposes_resilience() -> None:
    pipeline, _, _, _, resilience, *_ = create_pipeline()

    assert pipeline.resilience is resilience

def test_pipeline_exposes_event_bus() -> None:
    pipeline, _, _, _, _, event_bus, *_ = create_pipeline()

    assert pipeline.event_bus is event_bus

# ---------------------------------------------------------------------------
# Execution lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pipeline_executes_components_in_order() -> None:
    calls: list[str] = []

    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline(
        calls,
    )

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert isinstance(
        report,
        RuntimeReport,
    )

    assert calls == [
        "event:workflow.started",
        "scheduler",
        "event:workflow.scheduled",
        "monitor.begin",
        "resilience",
        "monitor.finish",
        "recovery",
        "event:workflow.finished",
    ]

@pytest.mark.asyncio
async def test_pipeline_returns_schedule_and_execution() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        schedule,
        execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert report.schedule is schedule
    assert report.execution is execution

@pytest.mark.asyncio
async def test_pipeline_passes_workflow_to_scheduler() -> None:
    (
        pipeline,
        scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    workflow = create_workflow()

    await pipeline.execute(
        workflow=workflow,
        context=create_task_context(),
    )

    assert scheduler.workflow is workflow

@pytest.mark.asyncio
async def test_pipeline_passes_schedule_to_resilience() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        resilience,
        _event_bus,
        schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert resilience.schedule is schedule

@pytest.mark.asyncio
async def test_pipeline_passes_workflow_to_resilience() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    workflow = create_workflow()

    await pipeline.execute(
        workflow=workflow,
        context=create_task_context(),
    )

    assert resilience.workflow is workflow

@pytest.mark.asyncio
async def test_pipeline_begins_monitoring_before_resilience() -> None:
    calls: list[str] = []

    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline(
        calls,
    )

    await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert calls.index(
        "monitor.begin",
    ) < calls.index(
        "resilience",
    )

@pytest.mark.asyncio
async def test_pipeline_finishes_monitoring_after_resilience() -> None:
    calls: list[str] = []

    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline(
        calls,
    )

    await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert calls.index(
        "resilience",
    ) < calls.index(
        "monitor.finish",
    )

@pytest.mark.asyncio
async def test_pipeline_passes_execution_result_to_monitor() -> None:
    (
        pipeline,
        _scheduler,
        monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert monitor.finish_result is execution

@pytest.mark.asyncio
async def test_pipeline_passes_context_to_resilience() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    context = create_task_context()

    await pipeline.execute(
        workflow=create_workflow(),
        context=context,
    )

    assert resilience.context is context

@pytest.mark.asyncio
async def test_pipeline_passes_context_to_recovery() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    context = create_task_context()

    await pipeline.execute(
        workflow=create_workflow(),
        context=context,
    )

    assert recovery.context is context

# ---------------------------------------------------------------------------
# Runtime report
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_runtime_report_contains_resilience_report() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert report.metadata["resilience"] is resilience_report

@pytest.mark.asyncio
async def test_runtime_report_contains_recovery_report() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert report.metadata["recovery"] is recovery_report

@pytest.mark.asyncio
async def test_runtime_report_contains_monitor_artifacts() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        metrics,
        trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert report.metadata["metrics"] is metrics
    assert report.metadata["trace"] is trace

@pytest.mark.asyncio
async def test_runtime_report_identifies_pipeline() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert report.metadata["runtime"] == (
        "WorkflowRuntimePipeline"
    )

# ---------------------------------------------------------------------------
# Runtime execution context
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_runtime_context_records_expected_events() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    runtime_context = cast(
        dict[str, object],
        report.metadata["runtime_context"],
    )

    events = cast(
        tuple[str, ...],
        runtime_context["events"],
    )

    assert events == (
        "workflow.started",
        "workflow.scheduled",
        "workflow.monitoring.started",
        "workflow.executed",
        "workflow.monitoring.finished",
        "workflow.recovery.completed",
        "workflow.finished",
    )

@pytest.mark.asyncio
async def test_runtime_context_records_state_keys() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    runtime_context = cast(
        dict[str, object],
        report.metadata["runtime_context"],
    )

    state_keys = cast(
        tuple[str, ...],
        runtime_context["state_keys"],
    )

    assert state_keys == (
        "schedule",
        "execution",
        "resilience",
        "metrics",
        "trace",
        "recovery",
    )

@pytest.mark.asyncio
async def test_runtime_context_identifies_workflow() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        _event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    report = await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    runtime_context = cast(
        dict[str, object],
        report.metadata["runtime_context"],
    )

    assert runtime_context["workflow"] == (
        "pipeline-test-workflow"
    )

# ---------------------------------------------------------------------------
# Event bus
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pipeline_publishes_lifecycle_events() -> None:
    (
        pipeline,
        _scheduler,
        _monitor,
        _recovery,
        _resilience,
        event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    await pipeline.execute(
        workflow=create_workflow(),
        context=create_task_context(),
    )

    assert [
        event.name
        for event in event_bus.events
    ] == [
        "workflow.started",
        "workflow.scheduled",
        "workflow.finished",
    ]

@pytest.mark.asyncio
async def test_event_bus_subscription_contract() -> None:
    event_bus = RecordingEventBus(
        calls=[],
    )

    listener = cast(
        WorkflowEventListener,
        Mock(),
    )

    await event_bus.subscribe(
        listener,
    )

    assert event_bus.listeners() == (
        listener,
    )

    await event_bus.unsubscribe(
        listener,
    )

    assert event_bus.listeners() == ()

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_workflow_fails_before_event_publication() -> None:
    (
        pipeline,
        scheduler,
        monitor,
        recovery,
        resilience,
        event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    workflow = Mock(
        spec=Workflow,
    )

    workflow.name = "invalid-workflow"
    workflow.validate = Mock(
        side_effect=ValueError(
            "invalid workflow",
        ),
    )

    with pytest.raises(
        ValueError,
        match="invalid workflow",
    ):
        await pipeline.execute(
            workflow=cast(
                Workflow,
                workflow,
            ),
            context=create_task_context(),
        )

    assert scheduler.workflow is None
    assert monitor.begin_workflow is None
    assert recovery.workflow is None
    assert resilience.workflow is None
    assert event_bus.events == []

# ---------------------------------------------------------------------------
# Failure propagation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_scheduler_failure_propagates() -> None:
    workflow = create_workflow()
    context = create_task_context()

    scheduler = Mock(
        spec=WorkflowScheduler,
    )

    scheduler.schedule = AsyncMock(
        side_effect=RuntimeError(
            "scheduling failed",
        ),
    )

    monitor = Mock(
        spec=WorkflowMonitor,
    )

    recovery = Mock(
        spec=WorkflowRecovery,
    )

    resilience = Mock(
        spec=WorkflowResilience,
    )

    event_bus = RecordingEventBus(
        calls=[],
    )

    pipeline = WorkflowRuntimePipeline(
        scheduler=cast(
            WorkflowScheduler,
            scheduler,
        ),
        monitor=cast(
            WorkflowMonitor,
            monitor,
        ),
        recovery=cast(
            WorkflowRecovery,
            recovery,
        ),
        resilience=cast(
            WorkflowResilience,
            resilience,
        ),
        event_bus=event_bus,
    )

    with pytest.raises(
        RuntimeError,
        match="scheduling failed",
    ):
        await pipeline.execute(
            workflow=workflow,
            context=context,
        )

    assert [
        event.name
        for event in event_bus.events
    ] == [
        "workflow.started",
    ]

    monitor.begin.assert_not_awaited()
    resilience.execute.assert_not_awaited()
    recovery.recover.assert_not_awaited()

@pytest.mark.asyncio
async def test_resilience_failure_propagates() -> None:
    workflow = create_workflow()
    context = create_task_context()
    schedule = create_schedule()

    scheduler = Mock(
        spec=WorkflowScheduler,
    )

    scheduler.schedule = AsyncMock(
        return_value=schedule,
    )

    monitor = Mock(
        spec=WorkflowMonitor,
    )

    monitor.begin = AsyncMock()

    resilience = Mock(
        spec=WorkflowResilience,
    )

    resilience.execute = AsyncMock(
        side_effect=RuntimeError(
            "execution failed",
        ),
    )

    recovery = Mock(
        spec=WorkflowRecovery,
    )

    event_bus = RecordingEventBus(
        calls=[],
    )

    pipeline = WorkflowRuntimePipeline(
        scheduler=cast(
            WorkflowScheduler,
            scheduler,
        ),
        monitor=cast(
            WorkflowMonitor,
            monitor,
        ),
        recovery=cast(
            WorkflowRecovery,
            recovery,
        ),
        resilience=cast(
            WorkflowResilience,
            resilience,
        ),
        event_bus=event_bus,
    )

    with pytest.raises(
        RuntimeError,
        match="execution failed",
    ):
        await pipeline.execute(
            workflow=workflow,
            context=context,
        )

    monitor.begin.assert_awaited_once_with(
        workflow=workflow,
    )

    resilience.execute.assert_awaited_once_with(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )

    recovery.recover.assert_not_awaited()

    assert [
        event.name
        for event in event_bus.events
    ] == [
        "workflow.started",
        "workflow.scheduled",
    ]

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def test_pipeline_diagnostics() -> None:
    (
        pipeline,
        scheduler,
        monitor,
        recovery,
        resilience,
        event_bus,
        _schedule,
        _execution,
        _metrics,
        _trace,
        _recovery_report,
        _resilience_report,
    ) = create_pipeline()

    diagnostics = pipeline.diagnostics()

    assert diagnostics == {
        "pipeline": "WorkflowRuntimePipeline",
        "scheduler": type(
            scheduler,
        ).__name__,
        "monitor": type(
            monitor,
        ).__name__,
        "recovery": type(
            recovery,
        ).__name__,
        "resilience": type(
            resilience,
        ).__name__,
        "event_bus": type(
            event_bus,
        ).__name__,
    }

# ---------------------------------------------------------------------------
# Execution context contract
# ---------------------------------------------------------------------------

def test_workflow_execution_context_is_available() -> None:
    """
    Ensure the runtime pipeline can construct the shared execution
    context using the current TaskContext contract.
    """

    workflow = create_workflow()
    task_context = create_task_context()

    context = WorkflowExecutionContext(
        workflow=workflow,
        task_context=task_context,
    )

    assert context.workflow is workflow
    assert context.task_context is task_context