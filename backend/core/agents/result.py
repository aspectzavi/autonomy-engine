"""
Agent execution result.

Defines the outcome of an autonomous agent execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime
from typing import Any

from backend.core.workflows.runtime_report import (
    RuntimeReport,
)


@dataclass(
    slots=True,
    frozen=True,
)
class AgentResult:
    """
    Result returned by an autonomous agent.
    """

    agent: str

    goal: str

    success: bool

    workflow_result: RuntimeReport | None = None

    output: Any = None

    error: str | None = None

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    finished_at: datetime | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def failed(
        self,
    ) -> bool:
        """
        Whether execution failed.
        """

        return not self.success

    @property
    def duration_seconds(
        self,
    ) -> float | None:
        """
        Total execution time.
        """

        if self.finished_at is None:
            return None

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # Factory Methods
    # ------------------------------------------------------------------

    @classmethod
    def ok(
        cls,
        *,
        agent: str,
        goal: str,
        workflow_result: RuntimeReport | None = None,
        output: Any = None,
        started_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AgentResult":
        """
        Create a successful result.
        """

        return cls(
            agent=agent,
            goal=goal,
            success=True,
            workflow_result=workflow_result,
            output=output,
            started_at=started_at
            or datetime.now(
                UTC,
            ),
            finished_at=datetime.now(
                UTC,
            ),
            metadata=metadata or {},
        )

    @classmethod
    def failure(
        cls,
        *,
        agent: str,
        goal: str,
        error: str,
        workflow_result: RuntimeReport | None = None,
        started_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AgentResult":
        """
        Create a failed result.
        """

        return cls(
            agent=agent,
            goal=goal,
            success=False,
            workflow_result=workflow_result,
            error=error,
            started_at=started_at
            or datetime.now(
                UTC,
            ),
            finished_at=datetime.now(
                UTC,
            ),
            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution diagnostics.
        """

        return {
            "agent": self.agent,
            "goal": self.goal,
            "success": self.success,
            "duration_seconds": (
                self.duration_seconds
            ),
            "workflow_success": (
                self.workflow_result.success
                if self.workflow_result
                is not None
                else None
            ),
            "metadata": self.metadata,
        }