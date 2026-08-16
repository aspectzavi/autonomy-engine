"""
In-memory vector store.

Default deterministic implementation of VectorStore.

Stores (MemoryEntry, embedding) pairs in a plain dict and performs
brute-force cosine-similarity search. Fine for development and
moderate memory volumes; intended to be swapped for a real vector
database (FAISS, Chroma, Qdrant, pgvector, ...) behind the same
VectorStore interface once one is needed.
"""

from __future__ import annotations

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.similarity import cosine_similarity
from backend.core.memory.vector_store import VectorStore


class InMemoryVectorStore(VectorStore):
    """
    Brute-force in-memory vector store.
    """

    def __init__(
        self,
    ) -> None:
        self._vectors: dict[
            str,
            tuple[MemoryEntry, list[float]],
        ] = {}

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def add(
        self,
        *,
        entry: MemoryEntry,
        embedding: list[float],
    ) -> None:
        """
        Store a memory entry together with its embedding.
        """

        self._vectors[entry.id] = (
            entry,
            embedding,
        )

    async def add_many(
        self,
        *,
        entries: list[MemoryEntry],
        embeddings: list[list[float]],
    ) -> None:
        """
        Store multiple memory entries.
        """

        if len(entries) != len(embeddings):
            raise ValueError(
                "entries and embeddings must have the same length.",
            )

        for entry, embedding in zip(
            entries,
            embeddings,
        ):
            await self.add(
                entry=entry,
                embedding=embedding,
            )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search(
        self,
        *,
        embedding: list[float],
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Return the most similar memory entries, most similar first.
        """

        scored = [
            (
                cosine_similarity(embedding, stored_embedding),
                entry,
            )
            for entry, stored_embedding in self._vectors.values()
        ]

        scored.sort(
            key=lambda pair: pair[0],
            reverse=True,
        )

        return [
            entry
            for _score, entry in scored[:limit]
        ]

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    async def remove(
        self,
        entry_id: str,
    ) -> None:
        """
        Remove a stored memory.
        """

        self._vectors.pop(
            entry_id,
            None,
        )

    async def clear(
        self,
    ) -> None:
        """
        Remove all stored vectors.
        """

        self._vectors.clear()

    async def count(
        self,
    ) -> int:
        """
        Return the number of stored vectors.
        """

        return len(self._vectors)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return vector store diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "vectors": len(self._vectors),
            },
        )

        return diagnostics
