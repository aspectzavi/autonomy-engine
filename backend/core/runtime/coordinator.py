"""
Runtime coordinator.

Coordinates autonomous runtime execution.

The coordinator is the primary entry point for executing user requests.
It orchestrates agent selection and execution without implementing
planning or workflow execution itself.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.runtime.dispatcher import RuntimeDispatcher
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.execution_session import (
    ExecutionSession,
)
from backend.core.runtime.execution_state import (
    ExecutionState,
)
from backend.core.kernel.runtime_context import RuntimeContext


class RuntimeCoordinator:
    """
    Coordinates autonomous runtime execution.
    """

    def __init__(
        self,
        *,
        dispatcher: RuntimeDispatcher,
        runtime_context: RuntimeContext,
    ) -> None:
        self._dispatcher = dispatcher
        self._runtime_context = runtime_context

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def dispatcher(
        self,
    ) -> RuntimeDispatcher:
        """
        Runtime dispatcher.
        """
        return self._dispatcher

    @property
    def runtime_context(
        self,
    ) -> RuntimeContext:
        """
        Shared runtime execution context.
        """
        return self._runtime_context

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Execute an autonomous runtime request.
        """

        session = ExecutionSession(
            request=request,
        )

        session.record(
            "Execution created.",
        )

        try:
            session.transition(
                ExecutionState.EXECUTING,
            )

            agent = self.dispatcher.dispatch(
                request,
            )

            session.record(
                f"Selected agent '{agent.name}'.",
            )

            task_context = (
                self.runtime_context.task_context()
            )

            agent_result = await agent.execute(
                goal=request.goal,
                task_context=task_context,
                context=AgentContext(),
            )

            if agent_result.success:
                session.transition(
                    ExecutionState.COMPLETED,
                )

                session.record(
                    "Execution completed.",
                )

            else:
                session.transition(
                    ExecutionState.FAILED,
                )

                session.record(
                    "Execution failed.",
                )

            return ExecutionResult(
                success=agent_result.success,
                workflow_result=agent_result.workflow_result,
                started_at=session.started_at,
                finished_at=(
                    session.completed_at
                    or session.updated_at
                ),
                errors=(
                    (agent_result.error,)
                    if agent_result.error
                    else ()
                ),
                metadata={
                    "request_id": request.request_id,
                    "agent": agent.name,
                    "events": tuple(
                        session.events,
                    ),
                },
            )

        except Exception as exc:
            session.transition(
                ExecutionState.FAILED,
            )

            session.record(
                str(exc),
            )

            return ExecutionResult(
                success=False,
                started_at=session.started_at,
                finished_at=(
                    session.completed_at
                    or session.updated_at
                ),
                errors=(
                    str(exc),
                ),
                metadata={
                    "request_id": (
                        request.request_id
                    ),
                    "events": tuple(
                        session.events,
                    ),
                },
            )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return coordinator diagnostics.
        """

        return {
            "dispatcher": (
                self.dispatcher.diagnostics()
            ),
            "runtime_context": (
                self.runtime_context.diagnostics()
            ),
        }