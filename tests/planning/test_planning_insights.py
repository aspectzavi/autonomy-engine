"""
Tests for PlanningInsights.
"""

from __future__ import annotations

from backend.core.planning.planning_insights import (
    PlanningInsights,
)


def test_planning_insights_empty() -> None:
    """
    A default PlanningInsights instance should be empty.
    """

    insights = PlanningInsights()

    assert insights.memory_count == 0
    assert insights.has_history is False
    assert insights.has_successful_history is False
    assert insights.has_failed_history is False
    assert insights.is_empty is True


def test_planning_insights_success_history() -> None:
    """
    Successful plans should be detected.
    """

    insights = PlanningInsights(
        memory_count=2,
        has_history=True,
        successful_plans=(
            "browser.search",
            "browser.login",
        ),
    )

    assert insights.has_history is True
    assert insights.has_successful_history is True
    assert insights.has_failed_history is False
    assert insights.is_empty is False


def test_planning_insights_failed_history() -> None:
    """
    Failed plans should be detected.
    """

    insights = PlanningInsights(
        memory_count=3,
        has_history=True,
        failed_plans=(
            "checkout",
        ),
    )

    assert insights.has_history is True
    assert insights.has_successful_history is False
    assert insights.has_failed_history is True
    assert insights.is_empty is False


def test_planning_insights_diagnostics() -> None:
    """
    Diagnostics should summarize the planning insights.
    """

    insights = PlanningInsights(
        memory_count=5,
        has_history=True,
        successful_plans=(
            "search",
            "summarize",
        ),
        failed_plans=(
            "checkout",
        ),
        suggested_capabilities=(
            "browser.search",
            "browser.open",
            "llm.reason",
        ),
        recommended_order=(
            "search",
            "reason",
            "execute",
        ),
        warnings=(
            "avoid duplicate login",
        ),
    )

    diagnostics = insights.diagnostics()

    assert diagnostics["memory_count"] == 5
    assert diagnostics["has_history"] is True
    assert diagnostics["successful_plans"] == 2
    assert diagnostics["failed_plans"] == 1
    assert diagnostics["suggested_capabilities"] == 3
    assert diagnostics["recommended_order"] == 3
    assert diagnostics["warnings"] == 1