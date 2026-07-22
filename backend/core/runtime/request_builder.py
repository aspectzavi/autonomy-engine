"""
Execution request builder.

Constructs fully populated execution requests from Goal objects.

The builder centralizes request creation so callers do not need to know
how an ExecutionRequest is assembled. Future enhancements such as
execution policies, priorities, deadlines, session identifiers, user
metadata, and tracing information can be added here without changing the
public execution API.
"""

from __future__ import annotations

from uuid import uuid4

from backend.core.agents.goal import Goal
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)


class RequestBuilder:
    """
    Builds runtime execution requests.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        goal: Goal,
        metadata: dict[str, object] | None = None,
    ) -> ExecutionRequest:
        """
        Build an execution request.

        Args:
            goal:
                Goal to execute.

            metadata:
                Optional execution metadata.

        Returns:
            A fully initialized ExecutionRequest.
        """

        return ExecutionRequest(
            request_id=str(uuid4()),
            goal=goal,
            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return builder diagnostics.
        """

        return {
            "goal_type": Goal.__name__,
            "request_id_strategy": "uuid4",
        }