"""
In-memory vector store tests.
"""

from __future__ import annotations

import pytest

from backend.core.memory.in_memory_vector_store import (
    InMemoryVectorStore,
)
from backend.core.memory.memory_entry import MemoryEntry


def _entry(entry_id: str, content: str = "x") -> MemoryEntry:
    return MemoryEntry(id=entry_id, content=content)


@pytest.mark.asyncio
async def test_search_ranks_by_cosine_similarity() -> None:
    store = InMemoryVectorStore()

    await store.add(entry=_entry("close"), embedding=[1.0, 0.0])
    await store.add(entry=_entry("far"), embedding=[0.0, 1.0])
    await store.add(entry=_entry("exact"), embedding=[0.9, 0.1])

    results = await store.search(embedding=[1.0, 0.0], limit=3)

    assert [entry.id for entry in results] == [
        "close",
        "exact",
        "far",
    ]


@pytest.mark.asyncio
async def test_search_respects_limit() -> None:
    store = InMemoryVectorStore()

    for i in range(5):
        await store.add(
            entry=_entry(str(i)),
            embedding=[1.0, 0.0],
        )

    results = await store.search(embedding=[1.0, 0.0], limit=2)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_add_many() -> None:
    store = InMemoryVectorStore()

    await store.add_many(
        entries=[_entry("a"), _entry("b")],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
    )

    assert await store.count() == 2


@pytest.mark.asyncio
async def test_add_many_rejects_mismatched_lengths() -> None:
    store = InMemoryVectorStore()

    with pytest.raises(ValueError):
        await store.add_many(
            entries=[_entry("a")],
            embeddings=[[1.0], [2.0]],
        )


@pytest.mark.asyncio
async def test_remove_and_clear() -> None:
    store = InMemoryVectorStore()

    await store.add(entry=_entry("a"), embedding=[1.0])
    await store.add(entry=_entry("b"), embedding=[1.0])

    await store.remove("a")
    assert await store.count() == 1

    await store.clear()
    assert await store.count() == 0


@pytest.mark.asyncio
async def test_remove_missing_entry_is_a_no_op() -> None:
    store = InMemoryVectorStore()

    await store.remove("does-not-exist")

    assert await store.count() == 0
