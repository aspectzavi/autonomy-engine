"""
Default workflow monitor tests.

Verifies that:

- begin() opens a real ExecutionTrace/TraceSpan through the shared
  Tracing service (not just the internal flat WorkflowTrace)
- finish() completes the span, marking it failed when the workflow
  execution reported failures
- diagnostics expose the execution_trace_id for cross-referencing
- existing WorkflowMetrics/WorkflowTrace behavior is unchanged
"""

from __future__ import annotations

import pytest

from backend.core.observability.tracing import Tracing
from backend.core.workflows.default_workflow_monitor import (
    DefaultWorkflowMonitor,
)
from backend.core.workflows.execution_result import ExecutionResult
from backend.core.workflows.workflow import Workflow


def _make_workflow() -> Workflow:
    return Workflow(name="monitor-test-workflow")


@pytest.mark.asyncio
async def test_begin_opens_a_real_execution_trace() -> None:
    tracing = Tracing()
    monitor = DefaultWorkflowMonitor(tracing=tracing)
    workflow = _make_workflow()

    await monitor.begin(workflow=workflow)

    assert monitor.execution_trace is not None
    assert monitor.execution_trace is tracing.get_trace(
        monitor.execution_trace.trace_id,
    )

    spans = monitor.execution_trace.spans
    assert len(spans) == 1
    assert spans[0].name == "workflow.monitor-test-workflow"
    assert not spans[0].completed


@pytest.mark.asyncio
async def test_finish_completes_the_span_on_success() -> None:
    tracing = Tracing()
    monitor = DefaultWorkflowMonitor(tracing=tracing)
    workflow = _make_workflow()

    await monitor.begin(workflow=workflow)

    result = ExecutionResult(
        success=True,
        completed_batches=2,
        completed_tasks=3,
        failed_tasks=0,
    )

    await monitor.finish(workflow=workflow, result=result)

    span = monitor.execution_trace.spans[0]
    assert span.completed
    assert not span.failed
    assert span.metadata["completed_tasks"] == 3


@pytest.mark.asyncio
async def test_finish_marks_span_failed_on_task_failures() -> None:
    tracing = Tracing()
    monitor = DefaultWorkflowMonitor(tracing=tracing)
    workflow = _make_workflow()

    await monitor.begin(workflow=workflow)

    result = ExecutionResult(
        success=False,
        completed_batches=1,
        completed_tasks=1,
        failed_tasks=1,
    )

    await monitor.finish(workflow=workflow, result=result)

    span = monitor.execution_trace.spans[0]
    assert span.completed
    assert span.failed
    assert span.error == "1 task(s) failed"


@pytest.mark.asyncio
async def test_diagnostics_expose_execution_trace_id() -> None:
    tracing = Tracing()
    monitor = DefaultWorkflowMonitor(tracing=tracing)
    workflow = _make_workflow()

    await monitor.begin(workflow=workflow)

    diagnostics = monitor.diagnostics()

    assert diagnostics["execution_trace_id"] == (
        monitor.execution_trace.trace_id
    )


def test_diagnostics_before_begin_has_no_trace_id() -> None:
    monitor = DefaultWorkflowMonitor(tracing=Tracing())

    diagnostics = monitor.diagnostics()

    assert diagnostics["execution_trace_id"] is None


@pytest.mark.asyncio
async def test_metrics_and_trace_still_populate() -> None:
    tracing = Tracing()
    monitor = DefaultWorkflowMonitor(tracing=tracing)
    workflow = _make_workflow()

    await monitor.begin(workflow=workflow)

    result = ExecutionResult(
        success=True,
        completed_batches=1,
        completed_tasks=1,
        failed_tasks=0,
    )

    await monitor.finish(workflow=workflow, result=result)

    metrics = monitor.metrics()
    trace = monitor.trace()

    assert metrics.workflow == "monitor-test-workflow"
    assert metrics.successful is True
    assert trace.is_finished
    assert trace.successful is True
