"""
Agent API routes.

Provides inspection endpoints for registered autonomous agents.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies.application import (
    get_application,
)
from backend.core.agents.registry import AgentRegistry
from backend.core.kernel.application import Application


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