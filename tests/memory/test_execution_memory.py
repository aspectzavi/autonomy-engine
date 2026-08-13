"""
ExecutionMemory tests.
"""

from __future__ import annotations

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_result import MemoryResult
from backend.core.runtime.execution_memory import ExecutionMemory


def test_attach_retrieved_memory() -> None:
    """
    Retrieved memories should be attached to the execution memory.
    """

    memory = ExecutionMemory()

    result = MemoryResult(
        entries=(
            MemoryEntry(
                id="1",
                content="Remember this",
                metadata={},
            ),
        ),
    )

    memory.attach(result)

    assert memory.retrieved is not None
    assert len(memory.retrieved.entries) == 1


def test_remember_generated_memory() -> None:
    """
    Generated memories should be queued for persistence.
    """

    memory = ExecutionMemory()

    entry = MemoryEntry(
        id="1",
        content="Generated memory",
        metadata={},
    )

    memory.remember(entry)

    assert len(memory.generated) == 1
    assert memory.generated[0] is entry


def test_variable_storage() -> None:
    """
    Temporary execution variables should be stored and retrieved.
    """

    memory = ExecutionMemory()

    memory.set(
        "attempt",
        3,
    )

    assert memory.get("attempt") == 3
    assert memory.get("missing") is None
    assert memory.get("missing", 42) == 42


def test_clear_variables() -> None:
    """
    Clearing variables should remove all temporary state.
    """

    memory = ExecutionMemory()

    memory.set(
        "x",
        1,
    )

    memory.set(
        "y",
        2,
    )

    memory.clear_variables()

    assert memory.variables == {}


def test_diagnostics_empty() -> None:
    """
    Diagnostics should report empty execution memory.
    """

    memory = ExecutionMemory()

    diagnostics = memory.diagnostics()

    assert diagnostics["retrieved"] == 0
    assert diagnostics["generated"] == 0
    assert diagnostics["variables"] == 0


def test_diagnostics_populated() -> None:
    """
    Diagnostics should reflect populated execution memory.
    """

    memory = ExecutionMemory()

    result = MemoryResult(
        entries=(
            MemoryEntry(
                id="1",
                content="Retrieved",
                metadata={},
            ),
            MemoryEntry(
                id="2",
                content="Retrieved again",
                metadata={},
            ),
        ),
    )

    memory.attach(result)

    memory.remember(
        MemoryEntry(
            id="3",
            content="Generated",
            metadata={},
        ),
    )

    memory.set(
        "goal",
        "search",
    )

    diagnostics = memory.diagnostics()

    assert diagnostics["retrieved"] == 2
    assert diagnostics["generated"] == 1
    assert diagnostics["variables"] == 1