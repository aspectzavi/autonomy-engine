
"""
Default workflow resilience.

Production-ready implementation of WorkflowResilience.

Coordinates workflow execution, retry handling, and failure
classification.

Current responsibilities:

- execute the supplied scheduling plan
- apply retry policy
- classify failures
- generate resilience reports

The scheduling plan is produced by the workflow runtime pipeline
before resilience execution begins.

Future versions may additionally support:

- circuit breakers
- adaptive retry
- checkpoint recovery
- workflow compensation
- distributed retries
- adaptive retry budgets
"""

from __future__ import annotations

import asyncio

from backend.core.tasks.context import TaskContext
from backend.core.workflows.execution_result import ExecutionResult
from backend.core.workflows.failure_classifier import FailureClassifier
from backend.core.workflows.resilience_report import ResilienceReport
from backend.core.workflows.retry_policy import RetryPolicy
from backend.core.workflows.scheduling_plan import SchedulingPlan
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_executor import WorkflowExecutor
from backend.core.workflows.workflow_resilience import WorkflowResilience


class DefaultWorkflowResilience(
    WorkflowResilience,
):
    """
    Default resilience implementation.

    The resilience layer does not perform scheduling. It receives
    an already-produced SchedulingPlan and applies execution,
    retry, and failure-classification policies around it.
    """

    def __init__(
        self,
        *,
        executor: WorkflowExecutor,
        retry_policy: RetryPolicy,
        failure_classifier: FailureClassifier,
        max_attempts: int = 3,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

        self._executor = executor
        self._retry_policy = retry_policy
        self._failure_classifier = failure_classifier
        self._max_attempts = max_attempts

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def executor(
        self,
    ) -> WorkflowExecutor:
        """
        Workflow executor.
        """

        return self._executor

    @property
    def retry_policy(
        self,
    ) -> RetryPolicy:
        """
        Retry policy.
        """

        return self._retry_policy

    @property
    def failure_classifier(
        self,
    ) -> FailureClassifier:
        """
        Failure classifier.
        """

        return self._failure_classifier

    @property
    def max_attempts(
        self,
    ) -> int:
        """
        Maximum number of execution attempts.
        """

        return self._max_attempts

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

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
        """
        Execute a workflow with resilience.

        The supplied scheduling plan is reused for every retry
        attempt. Scheduling is intentionally outside the resilience
        layer.

        Returns:
            Tuple containing the execution result and resilience report.
        """

        retries = 0

        while True:
            try:
                result = await self.executor.execute(
                    workflow=workflow,
                    schedule=schedule,
                    context=context,
                )

                report = ResilienceReport(
                    successful=result.success,
                    retry_attempts=self.max_attempts,
                    retries_performed=retries,
                    recovered=(
                        result.success
                        and retries > 0
                    ),
                    metadata={
                        "executor": (
                            type(
                                self.executor,
                            ).__name__
                        ),
                        "schedule": (
                            schedule.diagnostics()
                        ),
                    },
                )

                return (
                    result,
                    report,
                )

            except Exception as exc:
                decision = (
                    await self.retry_policy.decide(
                        error=exc,
                        attempt=retries + 1,
                        max_attempts=self.max_attempts,
                        context=context,
                    )
                )

                if not decision.should_retry:
                    report = ResilienceReport(
                        successful=False,
                        retry_attempts=self.max_attempts,
                        retries_performed=retries,
                        failure_classification=(
                            self.failure_classifier.classify(
                                exc,
                            )
                        ),
                        recovered=False,
                        metadata={
                            "reason": decision.reason,
                            "error": str(exc),
                            "schedule": (
                                schedule.diagnostics()
                            ),
                        },
                    )

                    return (
                        ExecutionResult(
                            success=False,
                            metadata={
                                "error": str(exc),
                                "retries": retries,
                            },
                        ),
                        report,
                    )

                retries += 1

                if decision.delay_seconds > 0:
                    await asyncio.sleep(
                        decision.delay_seconds,
                    )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return resilience diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "executor": (
                    self.executor.diagnostics()
                ),
                "retry_policy": (
                    self.retry_policy.diagnostics()
                ),
                "failure_classifier": (
                    self.failure_classifier.diagnostics()
                ),
                "max_attempts": self.max_attempts,
            },
        )

        return diagnostics
