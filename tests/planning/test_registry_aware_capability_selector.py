"""
Registry-aware capability selector tests.
"""

from __future__ import annotations

import pytest

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.capabilities.capability import Capability
from backend.core.capabilities.capability_provider import (
    CapabilityProvider,
)
from backend.core.capabilities.capability_registry import (
    CapabilityRegistry,
)
from backend.core.observability.events import EventBus
from backend.core.planning.planning_insights import PlanningInsights
from backend.core.planning.registry_aware_capability_selector import (
    RegistryAwareCapabilitySelector,
)
from backend.core.reasoning.decision import Decision
from backend.core.reasoning.reasoning_result import ReasoningResult
from backend.core.reasoning.reasoning_trace import ReasoningTrace


class _StubProvider(CapabilityProvider):
    def __init__(self, capabilities: tuple[Capability, ...]) -> None:
        self._capabilities = capabilities

    @property
    def name(self) -> str:
        return "stub"

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        return self._capabilities

    async def execute(self, capability, *, arguments=None):
        raise NotImplementedError


def _registry_with(*capabilities: Capability) -> CapabilityRegistry:
    registry = CapabilityRegistry()
    registry.register(_StubProvider(capabilities))
    return registry


def _reasoning(outcome: str = "execute") -> ReasoningResult:
    return ReasoningResult(
        strategy="test",
        decision=Decision(outcome=outcome, confidence=0.9),
        trace=ReasoningTrace(),
        confidence=0.9,
    )


def _context() -> AgentContext:
    return AgentContext(event_bus=EventBus())


@pytest.mark.asyncio
async def test_falls_back_to_abstract_placeholder_without_a_registry() -> None:
    selector = RegistryAwareCapabilitySelector(capability_registry=None)

    result = await selector.select(
        goal=Goal(description="do something"),
        context=_context(),
        reasoning=_reasoning("execute"),
        insights=PlanningInsights(),
    )

    assert result.capabilities == ("goal.execute", "goal.verify")


@pytest.mark.asyncio
async def test_falls_back_when_nothing_matches_well_enough() -> None:
    registry = _registry_with(
        Capability(
            name="browser_navigate",
            description="Navigate the browser to a URL.",
        ),
    )
    selector = RegistryAwareCapabilitySelector(
        capability_registry=registry,
    )

    result = await selector.select(
        goal=Goal(description="completely unrelated goal wording"),
        context=_context(),
        reasoning=_reasoning("execute"),
        insights=PlanningInsights(),
    )

    assert result.capabilities == ("goal.execute", "goal.verify")


@pytest.mark.asyncio
async def test_matches_a_real_capability_over_the_placeholder() -> None:
    registry = _registry_with(
        Capability(
            name="browser_navigate",
            description="Navigate the browser to a URL.",
        ),
    )
    selector = RegistryAwareCapabilitySelector(
        capability_registry=registry,
    )

    result = await selector.select(
        goal=Goal(description="navigate the browser to a url"),
        context=_context(),
        reasoning=_reasoning("execute"),
        insights=PlanningInsights(),
    )

    assert result.capabilities == ("browser_navigate", "goal.verify")
    assert result.metadata["matched_capability"] == "browser_navigate"


@pytest.mark.asyncio
async def test_picks_the_best_scoring_match_among_several() -> None:
    registry = _registry_with(
        Capability(
            name="browser_navigate",
            description="Navigate the browser to a URL.",
        ),
        Capability(
            name="desktop_click_element",
            description="Click an element in the connected window.",
        ),
    )
    selector = RegistryAwareCapabilitySelector(
        capability_registry=registry,
    )

    result = await selector.select(
        goal=Goal(
            description="click an element in the connected window",
        ),
        context=_context(),
        reasoning=_reasoning("execute"),
        insights=PlanningInsights(),
    )

    assert result.metadata["matched_capability"] == (
        "desktop_click_element"
    )


@pytest.mark.asyncio
async def test_preserves_non_execute_capabilities() -> None:
    registry = _registry_with(
        Capability(
            name="browser_navigate",
            description="Navigate the browser to a URL.",
        ),
    )
    selector = RegistryAwareCapabilitySelector(
        capability_registry=registry,
    )

    result = await selector.select(
        goal=Goal(description="navigate the browser to a url"),
        context=_context(),
        reasoning=_reasoning("clarify"),
        insights=PlanningInsights(),
    )

    #
    # "clarify" never selects "goal.execute" in the base selection,
    # so there is nothing for the registry match to replace.
    #
    assert result.capabilities == ("user.ask",)
