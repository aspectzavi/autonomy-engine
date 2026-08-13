"""
Semantic search.

Coordinates semantic retrieval across the embedding service and the
vector store.

SemanticSearch converts a text query into an embedding and retrieves
the most semantically similar memories.

The implementation intentionally contains no knowledge of embedding
providers or vector database implementations.
"""

from __future__ import annotations

from backend.core.memory.embedding_service import (
    EmbeddingService,
)
from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.vector_store import VectorStore


class SemanticSearch:
    """
    Semantic memory retrieval.
    """

    def __init__(
        self,
        *,
        embeddings: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self._embeddings = embeddings
        self._vector_store = vector_store

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def embeddings(
        self,
    ) -> EmbeddingService:
        """
        Embedding service.
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
    # Search
    # ------------------------------------------------------------------

    async def search(
        self,
        *,
        query: str,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Perform semantic memory retrieval.
        """

        embedding = await self.embeddings.embed(
            query,
        )

        return await self.vector_store.search(
            embedding=embedding,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return semantic search diagnostics.
        """

        return {
            "embedding_service": (
                self.embeddings.diagnostics()
            ),
            "vector_store": (
                self.vector_store.diagnostics()
            ),
        }