"""
Vector memory.

Concrete semantic-memory implementation of MemoryStore.

Every stored entry is embedded and indexed in a VectorStore. Queries
are answered via cosine-similarity search over those embeddings
instead of substring matching, so semantically related text (not just
exact word overlap) is retrieved.

The base in-memory dict inherited from MemoryStore is kept alongside
the vector index so delete()/clear()/size() stay correct and cheap
without needing extra bookkeeping.
"""

from __future__ import annotations

from backend.core.memory.embedding_service import (
    EmbeddingService,
)
from backend.core.memory.hashing_embedding_provider import (
    HashingEmbeddingProvider,
)
from backend.core.memory.in_memory_vector_store import (
    InMemoryVectorStore,
)
from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.memory_result import MemoryResult
from backend.core.memory.memory_store import MemoryStore
from backend.core.memory.semantic_search import SemanticSearch
from backend.core.memory.vector_store import VectorStore


class VectorMemory(MemoryStore):
    """
    Semantic vector memory.

    Drop-in MemoryStore replacement: same store()/query()/delete()/
    clear()/size() contract, backed by real embeddings and cosine
    similarity search instead of substring matching.
    """

    def __init__(
        self,
        *,
        embeddings: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        super().__init__()

        #
        # NOTE: `is None`, not `embeddings or EmbeddingService(...)`.
        # Kept consistent with the __len__ falsy-empty-collection
        # discipline used throughout this codebase, even though
        # neither EmbeddingService nor VectorStore implementations
        # define __len__ today.
        #
        self._embeddings = (
            embeddings
            if embeddings is not None
            else EmbeddingService(
                provider=HashingEmbeddingProvider(),
            )
        )

        self._vector_store = (
            vector_store
            if vector_store is not None
            else InMemoryVectorStore()
        )

        self._search = SemanticSearch(
            embeddings=self._embeddings,
            vector_store=self._vector_store,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def embeddings(
        self,
    ) -> EmbeddingService:
        """
        Embedding service used to index and query memories.
        """

        return self._embeddings

    @property
    def vector_store(
        self,
    ) -> VectorStore:
        """
        Vector storage backend.
        """

        return self._vector_store

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def store(
        self,
        entry: MemoryEntry,
    ) -> None:
        """
        Store a memory entry and index its embedding.
        """

        await super().store(
            entry,
        )

        embedding = await self.embeddings.embed(
            entry.content,
        )

        await self.vector_store.add(
            entry=entry,
            embedding=embedding,
        )

    async def query(
        self,
        query: MemoryQuery,
    ) -> MemoryResult:
        """
        Execute a semantic memory query.

        Falls back to an empty result rather than substring matching
        when the vector store is empty, so behavior stays predictable
        rather than silently reverting to a different retrieval
        strategy.
        """

        matches = await self._search.search(
            query=query.text,
            limit=query.limit,
        )

        return MemoryResult(
            entries=tuple(matches),
        )

    async def delete(
        self,
        entry_id: str,
    ) -> bool:
        """
        Delete a memory entry and its embedding.
        """

        deleted = await super().delete(
            entry_id,
        )

        await self.vector_store.remove(
            entry_id,
        )

        return deleted

    async def clear(
        self,
    ) -> None:
        """
        Remove every memory entry and embedding.
        """

        await super().clear()

        await self.vector_store.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Vector memory diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "memory_type": "vector",
                "embeddings": True,
                "embedding_service": (
                    self.embeddings.diagnostics()
                ),
                "vector_store": (
                    self.vector_store.diagnostics()
                ),
            },
        )

        return diagnostics
