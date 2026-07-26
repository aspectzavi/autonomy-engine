"""
Planning memory analyzer.

Extracts useful planning knowledge from retrieved execution memories.

This component isolates memory interpretation from planning logic.
"""

from __future__ import annotations

from backend.core.runtime.execution_memory import ExecutionMemory
from backend.core.planning.planning_insights import (
    PlanningInsights,
)

class PlanningMemoryAnalyzer:
    """
    Extracts planning hints from execution memory.
    """

    def analyze(
        self,
        memory: ExecutionMemory | None,
    ) -> PlanningInsights:
        """
        Analyze execution memory.

        Future implementations will:

        - identify similar goals
        - rank previous successful executions
        - detect repeated failures
        - recommend capabilities
        - recommend execution order

        Current implementation returns simple diagnostics.
        """

        if memory is None:
            return PlanningInsights()

        if memory.retrieved is None:
            return PlanningInsights()

        return PlanningInsights(
            memory_count=len(memory.retrieved.entries),
            has_history=bool(memory.retrieved.entries),
        )