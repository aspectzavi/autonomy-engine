"""
Tests for PlanningMemoryAnalyzer.
"""

from __future__ import annotations

from backend.core.planning.memory_analyzer import (
    PlanningMemoryAnalyzer,
)
from backend.core.runtime.execution_memory import (
    ExecutionMemory,
)
from backend.core.memory.memory_entry import (
    MemoryEntry,
)
from backend.core.memory.memory_result import (
    MemoryResult,
)


def test_analyze_none() -> None:
    """
    Analyzer should return empty planning insights when
    no execution memory is available.
    """

    analyzer = PlanningMemoryAnalyzer()

    insights = analyzer.analyze(
        None,
    )

    assert insights.memory_count == 0
    assert insights.has_history is False
    assert insights.is_empty is True


def test_analyze_empty_memory() -> None:
    """
    Analyzer should report no history for an empty memory result.
    """

    analyzer = PlanningMemoryAnalyzer()

    memory = ExecutionMemory()

    memory.attach(
        MemoryResult(
            entries=(),
        ),
    )

    insights = analyzer.analyze(
        memory,
    )

    assert insights.memory_count == 0
    assert insights.has_history is False
    assert insights.is_empty is True


def test_analyze_memory_with_entries() -> None:
    """
    Analyzer should report available execution history.
    """

    analyzer = PlanningMemoryAnalyzer()

    memory = ExecutionMemory()

    entry = MemoryEntry(
        id="memory-1",
        content="Previously solved login task.",
    )

    memory.attach(
        MemoryResult(
            entries=(
                entry,
            ),
        ),
    )

    insights = analyzer.analyze(
        memory,
    )

    assert insights.memory_count == 1
    assert insights.has_history is True
    assert insights.is_empty is False


def test_analyzer_does_not_modify_memory() -> None:
    """
    Analyzer should never mutate execution memory.
    """

    analyzer = PlanningMemoryAnalyzer()

    memory = ExecutionMemory()

    entry = MemoryEntry(
        id="memory-1",
        content="Remember successful workflow.",
    )

    result = MemoryResult(
        entries=(entry,),
    )

    memory.attach(
        result,
    )

    analyzer.analyze(
        memory,
    )

    retrieved = memory.retrieved

    assert retrieved is not None
    assert retrieved is result
    assert len(retrieved.entries) == 1