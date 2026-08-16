"""
Vector memory tests.

Verifies VectorMemory is a genuine drop-in MemoryStore replacement
backed by real embeddings and cosine-similarity search rather than
substring matching.
"""

from __future__ import annotations

import pytest

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.vector_memory import VectorMemory


@pytest.mark.asyncio
async def test_query_ranks_shared_vocabulary_above_unrelated_text() -> None:
    memory = VectorMemory()

    await memory.store(
        MemoryEntry(id="1", content="the cat sat on the warm windowsill in the sun"),
    )
    await memory.store(
        MemoryEntry(id="2", content="kittens love napping in sunny spots by the window"),
    )
    await memory.store(
        MemoryEntry(id="3", content="quarterly revenue grew twelve percent this year"),
    )

    result = await memory.query(
        MemoryQuery(text="cat sitting by a sunny window", limit=3),
    )

    ids = [entry.id for entry in result.entries]

    assert ids[-1] == "3"
    assert set(ids[:2]) == {"1", "2"}


@pytest.mark.asyncio
async def test_query_respects_limit() -> None:
    memory = VectorMemory()

    for i in range(5):
        await memory.store(
            MemoryEntry(id=str(i), content=f"shared word entry {i}"),
        )

    result = await memory.query(
        MemoryQuery(text="shared word", limit=2),
    )

    assert result.count == 2


@pytest.mark.asyncio
async def test_delete_removes_from_both_store_and_vector_index() -> None:
    memory = VectorMemory()

    await memory.store(
        MemoryEntry(id="1", content="a searchable memory"),
    )

    deleted = await memory.delete("1")
    assert deleted is True

    assert await memory.vector_store.count() == 0

    result = await memory.query(
        MemoryQuery(text="searchable memory"),
    )
    assert result.is_empty


@pytest.mark.asyncio
async def test_clear_removes_everything() -> None:
    memory = VectorMemory()

    await memory.store(MemoryEntry(id="1", content="one"))
    await memory.store(MemoryEntry(id="2", content="two"))

    await memory.clear()

    assert await memory.size() == 0
    assert await memory.vector_store.count() == 0


@pytest.mark.asyncio
async def test_query_on_empty_memory_returns_empty_result() -> None:
    memory = VectorMemory()

    result = await memory.query(MemoryQuery(text="anything"))

    assert result.is_empty


def test_diagnostics_report_embeddings_enabled() -> None:
    memory = VectorMemory()

    diagnostics = memory.diagnostics()

    assert diagnostics["embeddings"] is True
    assert diagnostics["memory_type"] == "vector"
