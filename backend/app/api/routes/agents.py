"""
Agent API routes.

Provides inspection endpoints for registered autonomous agents.
"""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from backend.app.api.dependencies.application import (
    get_application,
)
from backend.core.agents.goal import Goal
from backend.core.agents.registry import AgentRegistry
from backend.core.kernel.application import Application


class AgentExecutionRequest(BaseModel):
    """Request body for executing a goal through an agent."""

    agent: str = Field(
        default="planning",
        min_length=1,
        description="Registered agent name.",
    )
    description: str = Field(
        min_length=1,
        description="Natural-language goal for the agent.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Concrete tool arguments, such as url, selector, or path.",
    )
    priority: int = Field(
        default=0,
        description="Optional goal priority.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Optional execution constraints.",
    )


router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)


@router.get("")
async def list_agents(
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return all registered agents.
    """

    registry = app.container.resolve(
        AgentRegistry,
    )

    return {
        "agents": [
            agent.diagnostics()
            for agent in registry
        ],
    }


@router.get("/{name}")
async def get_agent(
    name: str,
    app: Application = Depends(get_application),
) -> dict[str, object]:
    """
    Return a single registered agent.
    """

    registry = app.container.resolve(
        AgentRegistry,
    )

    try:
        agent = registry.get(
            name,
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent '{name}'.",
        ) from None

    return agent.diagnostics()


@router.post("/execute")
async def execute_agent_goal(
    request: AgentExecutionRequest,
    app: Application = Depends(get_application),
) -> dict[str, Any]:
    """Execute a natural-language goal through a registered agent."""

    if not app.is_running:
        raise HTTPException(
            status_code=503,
            detail="The engine runtime is not running.",
        )

    if not app.agent_service.contains(request.agent):
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent '{request.agent}'.",
        )

    result = await app.agent_service.execute(
        agent=request.agent,
        goal=Goal(
            description=request.description,
            priority=request.priority,
            constraints=tuple(request.constraints),
            metadata=request.metadata,
        ),
        task_context=app.runtime.context.task_context(),
    )

    return cast(
        dict[str, Any],
        jsonable_encoder(
            {
                "agent": result.agent,
                "goal": result.goal,
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "started_at": result.started_at,
                "finished_at": result.finished_at,
                "duration_seconds": result.duration_seconds,
                "metadata": result.metadata,
                "workflow_result": result.workflow_result,
            }
        ),
    )
