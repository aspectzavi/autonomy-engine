"""
Rule-based workflow executor tests.

Verifies that:

- tasks within a single SchedulingGroup execute concurrently
- SchedulingGroups themselves execute in order
- failures are counted correctly and do not stop the batch
- diagnostics report parallel execution
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import Mock

import pytest

from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext
from backend.core.tasks.task import Task
from backend.core.workflows.rule_based_workflow_executor import (
    RuleBasedWorkflowExecutor,
)
from backend.core.workflows.scheduling_group import SchedulingGroup
from backend.core.workflows.scheduling_plan import SchedulingPlan
from backend.core.workflows.workflow import Workflow


def _make_context() -> TaskContext:
    return TaskContext(
        runtime=Mock(),
        container=Mock(),
        logger=Mock(spec=KernelLogger),
        events=EventBus(),
    )


class _SleepTask(Task):
    """Task that sleeps and records when it ran."""

    def __init__(self, name: str, delay: float, log: list[str]) -> None:
        super().__init__(name=name)
        self._delay = delay
        self._log = log

    async def run(self, context: TaskContext) -> object:
        await asyncio.sleep(self._delay)
        self._log.append(self.name)
        return None


class _FailingTask(Task):
    """Task whose run() raises."""

    async def run(self, context: TaskContext) -> object:
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_tasks_in_a_group_execute_concurrently() -> None:
    log: list[str] = []

    workflow = Workflow(name="parallel")
    workflow.add_task("a", _SleepTask("a", 0.05, log))
    workflow.add_task("b", _SleepTask("b", 0.05, log))

    schedule = SchedulingPlan(
        groups=(SchedulingGroup(node_ids=("a", "b")),),
    )

    executor = RuleBasedWorkflowExecutor()

    started = time.perf_counter()

    result = await executor.execute(
        workflow=workflow,
        schedule=schedule,
        context=_make_context(),
    )

    elapsed = time.perf_counter() - started

    assert result.success
    assert result.completed_tasks == 2
    # If tasks ran sequentially this would take >= 0.10s.
    assert elapsed < 0.09
    assert set(log) == {"a", "b"}


@pytest.mark.asyncio
async def test_groups_execute_in_order() -> None:
    log: list[str] = []

    workflow = Workflow(name="ordered")
    workflow.add_task("a", _SleepTask("a", 0.02, log))
    workflow.add_task("b", _SleepTask("b", 0.0, log))

    schedule = SchedulingPlan(
        groups=(
            SchedulingGroup(node_ids=("a",)),
            SchedulingGroup(node_ids=("b",)),
        ),
    )

    executor = RuleBasedWorkflowExecutor()

    result = await executor.execute(
        workflow=workflow,
        schedule=schedule,
        context=_make_context(),
    )

    assert result.success
    assert result.completed_batches == 2
    assert log == ["a", "b"]


@pytest.mark.asyncio
async def test_failed_task_is_counted_and_does_not_stop_batch() -> None:
    log: list[str] = []

    workflow = Workflow(name="with-failure")
    workflow.add_task("a", _FailingTask(name="a"))
    workflow.add_task("b", _SleepTask("b", 0.0, log))

    schedule = SchedulingPlan(
        groups=(SchedulingGroup(node_ids=("a", "b")),),
    )

    executor = RuleBasedWorkflowExecutor()

    result = await executor.execute(
        workflow=workflow,
        schedule=schedule,
        context=_make_context(),
    )

    assert not result.success
    assert result.completed_tasks == 1
    assert result.failed_tasks == 1
    assert log == ["b"]


@pytest.mark.asyncio
async def test_diagnostics_report_parallel_execution() -> None:
    executor = RuleBasedWorkflowExecutor()

    diagnostics = executor.diagnostics()

    assert diagnostics["parallel_execution"] is True
