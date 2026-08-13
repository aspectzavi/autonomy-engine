
"""
Workflow execution context tests.
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from unittest.mock import Mock

from backend.app.container.container import Container
from backend.core.kernel.runtime import Runtime
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_execution_context import (
    WorkflowExecutionContext,
)


def _create_task_context() -> TaskContext:
    """
    Create an isolated task context for workflow tests.
    """

    runtime = Mock(
        spec=Runtime,
    )

    return TaskContext(
        runtime=runtime,
        container=Container(),
        logger=KernelLogger(),
        events=EventBus(),
    )


def _create_workflow() -> Workflow:
    """
    Create a minimal workflow for context tests.
    """

    return Workflow(
        name="test-workflow",
    )


def _create_context() -> WorkflowExecutionContext:
    """
    Create a workflow execution context.
    """

    return WorkflowExecutionContext(
        workflow=_create_workflow(),
        task_context=_create_task_context(),
    )


def test_context_initialization() -> None:
    """
    Context should initialize with valid default runtime state.
    """

    context = _create_context()

    assert context.workflow.name == "test-workflow"
    assert context.task_context is not None

    assert isinstance(
        context.started_at,
        datetime,
    )

    assert context.started_at.tzinfo == UTC

    assert context.metadata == {}
    assert context.state == {}
    assert context.events == []
    assert context.errors == []

    assert context.retry_count == 0
    assert context.cancelled is False


def test_metadata_set_and_get() -> None:
    """
    Metadata should support storing and retrieving values.
    """

    context = _create_context()

    context.set(
        "request_id",
        "request-123",
    )

    context.set(
        "priority",
        10,
    )

    assert context.get(
        "request_id",
    ) == "request-123"

    assert context.get(
        "priority",
    ) == 10


def test_metadata_get_default() -> None:
    """
    Missing metadata should return the supplied default.
    """

    context = _create_context()

    assert context.get(
        "missing",
    ) is None

    assert context.get(
        "missing",
        "default",
    ) == "default"


def test_runtime_state() -> None:
    """
    Runtime state should support storing and retrieving values.
    """

    context = _create_context()

    context.put_state(
        "current_node",
        "node-a",
    )

    context.put_state(
        "attempt",
        2,
    )

    assert context.state_value(
        "current_node",
    ) == "node-a"

    assert context.state_value(
        "attempt",
    ) == 2


def test_runtime_state_default() -> None:
    """
    Missing runtime state should return the supplied default.
    """

    context = _create_context()

    assert context.state_value(
        "missing",
    ) is None

    assert context.state_value(
        "missing",
        "default",
    ) == "default"


def test_publish_event() -> None:
    """
    Published events should be recorded in execution order.
    """

    context = _create_context()

    context.publish(
        "workflow.started",
    )

    context.publish(
        "workflow.scheduled",
    )

    context.publish(
        "workflow.finished",
    )

    assert context.events == [
        "workflow.started",
        "workflow.scheduled",
        "workflow.finished",
    ]


def test_add_error() -> None:
    """
    Execution errors should be recorded.
    """

    context = _create_context()

    assert context.has_errors is False

    context.add_error(
        "execution failed",
    )

    context.add_error(
        "retry exhausted",
    )

    assert context.has_errors is True

    assert context.errors == [
        "execution failed",
        "retry exhausted",
    ]


def test_retry_tracking() -> None:
    """
    Retry count should increase when incremented.
    """

    context = _create_context()

    assert context.retry_count == 0

    context.increment_retry()

    assert context.retry_count == 1

    context.increment_retry()
    context.increment_retry()

    assert context.retry_count == 3


def test_cancellation() -> None:
    """
    Cancellation should mark the execution context as cancelled.
    """

    context = _create_context()

    assert context.cancelled is False

    context.cancel()

    assert context.cancelled is True


def test_diagnostics() -> None:
    """
    Diagnostics should expose the current execution state.
    """

    context = _create_context()

    context.set(
        "request_id",
        "request-123",
    )

    context.put_state(
        "current_node",
        "node-a",
    )

    context.publish(
        "workflow.started",
    )

    context.add_error(
        "test error",
    )

    context.increment_retry()
    context.cancel()

    diagnostics = context.diagnostics()

    assert diagnostics["workflow"] == "test-workflow"

    assert diagnostics["retry_count"] == 1

    assert diagnostics["cancelled"] is True

    assert diagnostics["metadata"] == {
        "request_id": "request-123",
    }

    assert diagnostics["state_keys"] == (
        "current_node",
    )

    assert diagnostics["events"] == (
        "workflow.started",
    )

    assert diagnostics["errors"] == (
        "test error",
    )


def test_metadata_and_state_are_isolated() -> None:
    """
    Metadata and runtime state should remain separate namespaces.
    """

    context = _create_context()

    context.set(
        "value",
        "metadata",
    )

    context.put_state(
        "value",
        "state",
    )

    assert context.get(
        "value",
    ) == "metadata"

    assert context.state_value(
        "value",
    ) == "state"

    assert context.metadata == {
        "value": "metadata",
    }

    assert context.state == {
        "value": "state",
    }


def test_events_and_errors_are_ordered() -> None:
    """
    Events and errors should preserve insertion order.
    """

    context = _create_context()

    context.publish("event-1")
    context.publish("event-2")
    context.publish("event-3")

    context.add_error("error-1")
    context.add_error("error-2")

    assert context.events == [
        "event-1",
        "event-2",
        "event-3",
    ]

    assert context.errors == [
        "error-1",
        "error-2",
    ]


def test_started_at_is_timezone_aware() -> None:
    """
    Execution timestamps should always be timezone-aware.
    """

    context = _create_context()

    assert context.started_at.tzinfo is not None
    assert context.started_at.utcoffset() is not None
