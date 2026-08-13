
"""
Workflow service registration.

Registers the complete workflow subsystem into the dependency injection
container.

This module acts as the composition root for workflow execution. It
constructs the scheduler, executor, monitoring, recovery, resilience,
event bus, and runtime, allowing WorkflowService to depend only on the
WorkflowRuntime abstraction.
"""

from __future__ import annotations

from typing import Any
from typing import cast

from backend.app.container.container import Container

from backend.core.services.workflow_service import WorkflowService

from backend.core.workflows.workflow_runtime import (
    WorkflowRuntime,
)
from backend.core.workflows.default_workflow_runtime import (
    DefaultWorkflowRuntime,
)

from backend.core.workflows.workflow_scheduler import (
    WorkflowScheduler,
)
from backend.core.workflows.rule_based_workflow_scheduler import (
    RuleBasedWorkflowScheduler,
)

from backend.core.workflows.workflow_executor import (
    WorkflowExecutor,
)
from backend.core.workflows.rule_based_workflow_executor import (
    RuleBasedWorkflowExecutor,
)

from backend.core.workflows.workflow_monitor import (
    WorkflowMonitor,
)
from backend.core.workflows.default_workflow_monitor import (
    DefaultWorkflowMonitor,
)

from backend.core.workflows.workflow_recovery import (
    WorkflowRecovery,
)
from backend.core.workflows.default_workflow_recovery import (
    DefaultWorkflowRecovery,
)

from backend.core.workflows.workflow_resilience import (
    WorkflowResilience,
)
from backend.core.workflows.default_workflow_resilience import (
    DefaultWorkflowResilience,
)

from backend.core.workflows.retry_policy import (
    RetryPolicy,
)
from backend.core.workflows.rule_based_retry_policy import (
    RuleBasedRetryPolicy,
)

from backend.core.workflows.failure_classifier import (
    FailureClassifier,
)

from backend.core.workflows.workflow_event_bus import (
    WorkflowEventBus,
)
from backend.core.workflows.in_memory_workflow_event_bus import (
    InMemoryWorkflowEventBus,
)


def register_workflow_services(
    container: Container,
) -> None:
    """
    Register the complete workflow subsystem.
    """

    # ------------------------------------------------------------------
    # Scheduler
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowScheduler,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowScheduler,
            ),
            implementation=RuleBasedWorkflowScheduler,
        )

    # ------------------------------------------------------------------
    # Executor
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowExecutor,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowExecutor,
            ),
            implementation=RuleBasedWorkflowExecutor,
        )

    # ------------------------------------------------------------------
    # Retry policy
    # ------------------------------------------------------------------

    if not container.contains(
        RetryPolicy,
    ):
        container.register_singleton(
            cast(
                type[Any],
                RetryPolicy,
            ),
            implementation=RuleBasedRetryPolicy,
        )

    # ------------------------------------------------------------------
    # Failure classifier
    # ------------------------------------------------------------------

    if not container.contains(
        FailureClassifier,
    ):
        container.register_singleton(
            cast(
                type[Any],
                FailureClassifier,
            ),
            implementation=FailureClassifier,
        )

    # ------------------------------------------------------------------
    # Monitor
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowMonitor,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowMonitor,
            ),
            implementation=DefaultWorkflowMonitor,
        )

    # ------------------------------------------------------------------
    # Recovery
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowRecovery,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowRecovery,
            ),
            implementation=DefaultWorkflowRecovery,
        )

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowEventBus,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowEventBus,
            ),
            implementation=InMemoryWorkflowEventBus,
        )

    # ------------------------------------------------------------------
    # Resilience
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowResilience,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowResilience,
            ),
            implementation=DefaultWorkflowResilience,
        )

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowRuntime,
    ):
        container.register_singleton(
            cast(
                type[Any],
                WorkflowRuntime,
            ),
            implementation=DefaultWorkflowRuntime,
        )

    # ------------------------------------------------------------------
    # Workflow service
    # ------------------------------------------------------------------

    if not container.contains(
        WorkflowService,
    ):
        container.register_singleton(
            WorkflowService,
        )
