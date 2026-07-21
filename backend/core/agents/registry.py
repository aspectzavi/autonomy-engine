"""
Agent registry.

Stores and resolves autonomous agents by name.
"""

from __future__ import annotations

from typing import Iterator

from backend.core.agents.agent import Agent
from backend.core.agents.exceptions import (
    AgentAlreadyRegisteredError,
    AgentNotFoundError,
)


class AgentRegistry:
    """
    Registry of autonomous agents.

    Provides registration and lookup functionality without managing
    execution or lifecycle.
    """

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        agent: Agent,
    ) -> None:
        """
        Register an agent.

        Raises:
            ValueError:
                If an agent with the same name already exists.
        """
        if agent.name in self._agents:
            raise AgentAlreadyRegisteredError(
                f"Agent '{agent.name}' is already registered."
            )

        self._agents[agent.name] = agent

    def unregister(
        self,
        name: str,
    ) -> Agent:
        """
        Remove and return an agent.

        Raises:
            KeyError:
                If the agent is not registered.
        """
        try:
            return self._agents.pop(name)
        except KeyError as exc:
            raise AgentNotFoundError(
                f"Agent '{name}' is not registered."
            ) from exc

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Agent:
        """
        Return a registered agent.

        Raises:
            KeyError:
                If the agent is not registered.
        """
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(
                f"Agent '{name}' is not registered."
            ) from exc

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Whether an agent is registered.
        """
        return name in self._agents

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    def agents(self) -> tuple[Agent, ...]:
        """
        Return all registered agents.
        """
        return tuple(self._agents.values())

    def names(self) -> tuple[str, ...]:
        """
        Return registered agent names.
        """
        return tuple(self._agents.keys())

    def clear(self) -> None:
        """
        Remove all registered agents.
        """
        self._agents.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return registry diagnostics.
        """
        return {
            "agent_count": len(self),
            "agents": [
                {
                    "name": agent.name,
                    "state": agent.state.value,
                    "type": type(agent).__name__,
                }
                for agent in self._agents.values()
            ],
        }

    # ------------------------------------------------------------------
    # Dunder Methods
    # ------------------------------------------------------------------

    def __contains__(
        self,
        name: object,
    ) -> bool:
        """
        Whether an agent is registered.
        """
        return (
            isinstance(name, str)
            and name in self._agents
        )

    def __len__(self) -> int:
        """
        Number of registered agents.
        """
        return len(self._agents)

    def __iter__(self) -> Iterator[Agent]:
        """
        Iterate over registered agents.
        """
        return iter(self._agents.values())