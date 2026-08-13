"""
Retry middleware.

Provides retry behavior for workflow execution.

The middleware delegates retry decisions to the configured RetryPolicy
and records retry information inside the MiddlewareContext.

Responsibilities:

- execute workflow
- consult RetryPolicy
- retry failed executions
- expose retry metadata

Future implementations may additionally support:

- exponential backoff
- jitter
- retry budgets
- adaptive retry strategies
- distributed retry coordination
"""

from __future__ import annotations

import asyncio

from backend.core.workflows.failure_classifier import (
    FailureClassifier,
)
from backend.core.workflows.middleware.middleware_context import (
    MiddlewareContext,
)
from backend.core.workflows.middleware.workflow_middleware import (
    NextMiddleware,
    WorkflowMiddleware,
)
from backend.core.workflows.retry_policy import (
    RetryPolicy,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)


class RetryMiddleware(
    WorkflowMiddleware,
):
    """
    Default retry middleware.
    """

    RETRY_KEY = "workflow.retry"

    def __init__(
        self,
        *,
        retry_policy: RetryPolicy,
        failure_classifier: FailureClassifier,
        max_attempts: int = 3,
    ) -> None:
        self._retry_policy = retry_policy
        self._failure_classifier = (
            failure_classifier
        )
        self._max_attempts = max_attempts

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def retry_policy(
        self,
    ) -> RetryPolicy:
        return self._retry_policy

    @property
    def failure_classifier(
        self,
    ) -> FailureClassifier:
        return self._failure_classifier

    @property
    def max_attempts(
        self,
    ) -> int:
        return self._max_attempts

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextMiddleware,
    ) -> RuntimeReport:
        """
        Execute workflow with retry support.
        """

        attempt = 1

        while True:
            try:
                report = await next_handler(
                    context,
                )

                context.set(
                    self.RETRY_KEY,
                    {
                        "attempts": attempt,
                        "retried": attempt > 1,
                    },
                )

                return report

            except Exception as exc:
                decision = await self.retry_policy.decide(
                    error=exc,
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                    context=context.task_context,
                )

                if not decision.should_retry:
                    context.set(
                        self.RETRY_KEY,
                        {
                            "attempts": attempt,
                            "retried": attempt > 1,
                            "classification": (
                                self.failure_classifier.classify(
                                    exc,
                                )
                            ),
                            "reason": (
                                decision.reason
                            ),
                        },
                    )

                    raise

                if decision.delay_seconds > 0:
                    await asyncio.sleep(
                        decision.delay_seconds,
                    )

                attempt += 1

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "retry_policy": (
                    type(
                        self.retry_policy,
                    ).__name__
                ),
                "failure_classifier": (
                    type(
                        self.failure_classifier,
                    ).__name__
                ),
                "max_attempts": (
                    self.max_attempts
                ),
            },
        )

        return diagnostics