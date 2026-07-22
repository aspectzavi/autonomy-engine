"""
Runtime dispatcher.

Routes execution requests to autonomous agents.

The dispatcher owns agent selection but does not perform planning
or execution itself.
"""

from __future__ import annotations

from backend.core.agents.agent import Agent
from backend.core.services.agent_service import AgentService
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)


class RuntimeDispatcher:
    """
    Dispatch execution requests to agents.
    """

    def __init__(
        self,
        agent_service: AgentService,
    ) -> None:
        self._agent_service = agent_service

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def agent_service(
        self,
    ) -> AgentService:
        """
        Runtime agent service.
        """
        return self._agent_service

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch(
        self,
        request: ExecutionRequest,
    ) -> Agent:
        """
        Select the agent responsible for handling an execution request.

        Currently returns the default planning agent.

        Future implementations may perform:

        - capability matching
        - model selection
        - multi-agent routing
        - workload balancing
        """

        del request

        return self.agent_service.get(
            "planning",
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return dispatcher diagnostics.
        """

        return {
            "agent_service": type(
                self.agent_service,
            ).__name__,
        }