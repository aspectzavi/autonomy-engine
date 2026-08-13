
"""
Default workflow resilience tests.

Tests the execution, retry, failure-classification, and diagnostics
contracts of DefaultWorkflowResilience.

The resilience layer receives an already-produced SchedulingPlan.
Scheduling is intentionally owned by the workflow runtime pipeline.
"""

from __future__ import annotations

import asyncio
from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from backend.app.container.container import Container
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext
from backend.core.workflows.execution_result import ExecutionResult
from backend.core.workflows.failure_classifier import (
    FailureClassifier,
)
from backend.core.workflows.resilience_report import ResilienceReport
from backend.core.workflows.retry_policy import RetryPolicy
from backend.core.workflows.scheduling_plan import SchedulingPlan
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_executor import WorkflowExecutor
from backend.core.workflows.default_workflow_resilience import (
    DefaultWorkflowResilience,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def create_workflow() -> Workflow:
    """Create a minimal valid workflow."""
    return Workflow(
        name="resilience-test-workflow",
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

    The resilience layer receives this plan and passes it directly
    to the executor.
    """
    schedule = Mock(
        spec=SchedulingPlan,
    )

    schedule.diagnostics.return_value = {
        "plan": "test-plan",
    }

    return cast(
        SchedulingPlan,
        schedule,
    )


def create_execution_result(
    *,
    success: bool = True,
) -> ExecutionResult:
    """Create an opaque execution result."""
    result = Mock(
        spec=ExecutionResult,
    )

    result.success = success

    return cast(
        ExecutionResult,
        result,
    )


def create_resilience(
    *,
    executor: WorkflowExecutor,
    retry_policy: RetryPolicy | None = None,
    failure_classifier: FailureClassifier | None = None,
    max_attempts: int = 3,
) -> DefaultWorkflowResilience:
    """
    Create an isolated DefaultWorkflowResilience.

    The executor, retry policy, and failure classifier are supplied
    explicitly so scheduling remains outside the resilience layer.
    """

    if retry_policy is None:
        retry_policy = cast(
            RetryPolicy,
            Mock(
                spec=RetryPolicy,
            ),
        )

    if failure_classifier is None:
        failure_classifier = cast(
            FailureClassifier,
            Mock(
                spec=FailureClassifier,
            ),
        )

    return DefaultWorkflowResilience(
        executor=executor,
        retry_policy=retry_policy,
        failure_classifier=failure_classifier,
        max_attempts=max_attempts,
    )


# ---------------------------------------------------------------------------
# Properties / construction
# ---------------------------------------------------------------------------


def test_resilience_exposes_executor() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
    )

    assert resilience.executor is executor


def test_resilience_exposes_retry_policy() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
    )

    assert resilience.retry_policy is retry_policy


def test_resilience_exposes_failure_classifier() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    classifier = Mock(
        spec=FailureClassifier,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        failure_classifier=cast(
            FailureClassifier,
            classifier,
        ),
    )

    assert resilience.failure_classifier is classifier


def test_resilience_exposes_max_attempts() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        max_attempts=5,
    )

    assert resilience.max_attempts == 5


def test_invalid_max_attempts_is_rejected() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    with pytest.raises(
        ValueError,
        match="max_attempts must be at least 1",
    ):
        create_resilience(
            executor=cast(
                WorkflowExecutor,
                executor,
            ),
            max_attempts=0,
        )


# ---------------------------------------------------------------------------
# Successful execution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_successful_execution_passes_supplied_schedule_to_executor() -> None:
    workflow = create_workflow()
    context = create_task_context()
    schedule = create_schedule()
    execution = create_execution_result(
        success=True,
    )

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        return_value=execution,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
    )

    result, report = await resilience.execute(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )

    assert result is execution
    assert isinstance(
        report,
        ResilienceReport,
    )

    executor.execute.assert_awaited_once_with(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )


@pytest.mark.asyncio
async def test_successful_execution_does_not_schedule() -> None:
    """
    Scheduling is owned by WorkflowRuntimePipeline.

    DefaultWorkflowResilience must never attempt to create a schedule.
    """

    workflow = create_workflow()
    context = create_task_context()
    schedule = create_schedule()
    execution = create_execution_result()

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        return_value=execution,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
    )

    await resilience.execute(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )

    executor.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_successful_execution_generates_successful_report() -> None:
    execution = create_execution_result(
        success=True,
    )

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        return_value=execution,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
    )

    result, report = await resilience.execute(
        workflow=create_workflow(),
        schedule=create_schedule(),
        context=create_task_context(),
    )

    assert result is execution
    assert report.successful is True
    assert report.retries_performed == 0
    assert report.recovered is False
    assert report.retry_attempts == resilience.max_attempts


@pytest.mark.asyncio
async def test_successful_execution_includes_executor_metadata() -> None:
    execution = create_execution_result()

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        return_value=execution,
    )

    schedule = create_schedule()

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
    )

    _, report = await resilience.execute(
        workflow=create_workflow(),
        schedule=schedule,
        context=create_task_context(),
    )

    assert report.metadata["executor"] == (
        type(executor).__name__
    )

    assert report.metadata["schedule"] == {
        "plan": "test-plan",
    }


# ---------------------------------------------------------------------------
# Retry behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_reuses_same_schedule() -> None:
    workflow = create_workflow()
    context = create_task_context()
    schedule = create_schedule()

    first_failure = RuntimeError(
        "temporary failure",
    )

    execution = create_execution_result()

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=[
            first_failure,
            execution,
        ],
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    decision = Mock()
    decision.should_retry = True
    decision.delay_seconds = 0
    decision.reason = "transient_failure"

    retry_policy.decide = AsyncMock(
        return_value=decision,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
    )

    result, report = await resilience.execute(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )

    assert result is execution

    assert executor.execute.await_count == 2

    assert executor.execute.await_args_list[0].kwargs[
        "schedule"
    ] is schedule

    assert executor.execute.await_args_list[1].kwargs[
        "schedule"
    ] is schedule

    assert report.retries_performed == 1
    assert report.recovered is True


@pytest.mark.asyncio
async def test_retry_policy_receives_correct_attempt_numbers() -> None:
    workflow = create_workflow()
    context = create_task_context()
    schedule = create_schedule()

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=[
            RuntimeError("first failure"),
            RuntimeError("second failure"),
            create_execution_result(),
        ],
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    first_decision = Mock()
    first_decision.should_retry = True
    first_decision.delay_seconds = 0
    first_decision.reason = "retry"

    second_decision = Mock()
    second_decision.should_retry = True
    second_decision.delay_seconds = 0
    second_decision.reason = "retry"

    retry_policy.decide = AsyncMock(
        side_effect=[
            first_decision,
            second_decision,
        ],
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
        max_attempts=3,
    )

    await resilience.execute(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )

    assert retry_policy.decide.await_count == 2

    assert retry_policy.decide.await_args_list[0].kwargs[
        "attempt"
    ] == 1

    assert retry_policy.decide.await_args_list[1].kwargs[
        "attempt"
    ] == 2

    assert (
        retry_policy.decide.await_args_list[0].kwargs[
            "max_attempts"
        ]
        == 3
    )


@pytest.mark.asyncio
async def test_retry_policy_receives_context() -> None:
    context = create_task_context()

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=RuntimeError(
            "temporary failure",
        ),
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    decision = Mock()
    decision.should_retry = False
    decision.delay_seconds = 0
    decision.reason = "not_retryable"

    retry_policy.decide = AsyncMock(
        return_value=decision,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
    )

    await resilience.execute(
        workflow=create_workflow(),
        schedule=create_schedule(),
        context=context,
    )

    retry_policy.decide.assert_awaited_once()

    assert retry_policy.decide.await_args.kwargs[
        "context"
    ] is context


@pytest.mark.asyncio
async def test_retry_delay_is_applied() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=[
            RuntimeError("temporary failure"),
            create_execution_result(),
        ],
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    decision = Mock()
    decision.should_retry = True
    decision.delay_seconds = 0.25
    decision.reason = "retry"

    retry_policy.decide = AsyncMock(
        return_value=decision,
    )

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
    )

    sleep = AsyncMock()

    original_sleep = asyncio.sleep

    try:
        asyncio.sleep = sleep

        await resilience.execute(
            workflow=create_workflow(),
            schedule=create_schedule(),
            context=create_task_context(),
        )
    finally:
        asyncio.sleep = original_sleep

    sleep.assert_awaited_once_with(
        0.25,
    )


# ---------------------------------------------------------------------------
# Failure handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_retryable_failure_returns_failed_execution() -> None:
    workflow = create_workflow()
    context = create_task_context()
    schedule = create_schedule()

    error = RuntimeError(
        "permanent failure",
    )

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=error,
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    decision = Mock()
    decision.should_retry = False
    decision.delay_seconds = 0
    decision.reason = "permanent_failure"

    retry_policy.decide = AsyncMock(
        return_value=decision,
    )

    classifier = Mock(
        spec=FailureClassifier,
    )

    classification = "non_retryable"

    classifier.classify.return_value = classification

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
        failure_classifier=cast(
            FailureClassifier,
            classifier,
        ),
    )

    result, report = await resilience.execute(
        workflow=workflow,
        schedule=schedule,
        context=context,
    )

    assert result.success is False
    assert result.metadata["error"] == (
        "permanent failure"
    )
    assert result.metadata["retries"] == 0

    assert report.successful is False
    assert report.retries_performed == 0
    assert report.recovered is False
    assert report.failure_classification == classification

    classifier.classify.assert_called_once_with(
        error,
    )


@pytest.mark.asyncio
async def test_failure_metadata_contains_schedule_diagnostics() -> None:
    error = RuntimeError(
        "permanent failure",
    )

    schedule = create_schedule()

    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=error,
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    decision = Mock()
    decision.should_retry = False
    decision.delay_seconds = 0
    decision.reason = "not_retryable"

    retry_policy.decide = AsyncMock(
        return_value=decision,
    )

    classifier = Mock(
        spec=FailureClassifier,
    )

    classifier.classify.return_value = "permanent"

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
        failure_classifier=cast(
            FailureClassifier,
            classifier,
        ),
    )

    _, report = await resilience.execute(
        workflow=create_workflow(),
        schedule=schedule,
        context=create_task_context(),
    )

    assert report.metadata["schedule"] == {
        "plan": "test-plan",
    }

    assert report.metadata["reason"] == (
        "not_retryable"
    )

    assert report.metadata["error"] == (
        "permanent failure"
    )


@pytest.mark.asyncio
async def test_failure_after_retries_reports_retry_count() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    executor.execute = AsyncMock(
        side_effect=[
            RuntimeError("failure one"),
            RuntimeError("failure two"),
            RuntimeError("failure three"),
        ],
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    decisions = []

    for _ in range(2):
        decision = Mock()
        decision.should_retry = True
        decision.delay_seconds = 0
        decision.reason = "retry"

        decisions.append(decision)

    final_decision = Mock()
    final_decision.should_retry = False
    final_decision.delay_seconds = 0
    final_decision.reason = "retry_budget_exhausted"

    decisions.append(
        final_decision,
    )

    retry_policy.decide = AsyncMock(
        side_effect=decisions,
    )

    classifier = Mock(
        spec=FailureClassifier,
    )

    classifier.classify.return_value = "retry_exhausted"

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
        failure_classifier=cast(
            FailureClassifier,
            classifier,
        ),
        max_attempts=3,
    )

    result, report = await resilience.execute(
        workflow=create_workflow(),
        schedule=create_schedule(),
        context=create_task_context(),
    )

    assert result.success is False
    assert result.metadata["retries"] == 2

    assert report.retries_performed == 2
    assert report.recovered is False
    assert report.successful is False
    assert report.failure_classification == (
        "retry_exhausted"
    )

    assert executor.execute.await_count == 3


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def test_resilience_diagnostics() -> None:
    executor = Mock(
        spec=WorkflowExecutor,
    )

    retry_policy = Mock(
        spec=RetryPolicy,
    )

    classifier = Mock(
        spec=FailureClassifier,
    )

    executor.diagnostics.return_value = {
        "executor": "test",
    }

    retry_policy.diagnostics.return_value = {
        "retry_policy": "test",
    }

    classifier.diagnostics.return_value = {
        "failure_classifier": "test",
    }

    resilience = create_resilience(
        executor=cast(
            WorkflowExecutor,
            executor,
        ),
        retry_policy=cast(
            RetryPolicy,
            retry_policy,
        ),
        failure_classifier=cast(
            FailureClassifier,
            classifier,
        ),
        max_attempts=4,
    )

    diagnostics = resilience.diagnostics()

    assert diagnostics == {
        "resilience": "DefaultWorkflowResilience",
        "executor": {
            "executor": "test",
        },
        "retry_policy": {
            "retry_policy": "test",
        },
        "failure_classifier": {
            "failure_classifier": "test",
        },
        "max_attempts": 4,
    }
