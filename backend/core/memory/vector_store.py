"""
Vector store.

Defines the abstract interface for semantic vector storage.

A vector store indexes embeddings and supports similarity search.

Concrete implementations may use:

- FAISS
- ChromaDB
- Qdrant
- Pinecone
- Milvus
- Weaviate
- PostgreSQL + pgvector
- SQLite extensions

The runtime depends only on this interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.memory.memory_entry import MemoryEntry


class VectorStore(ABC):
    """
    Base interface for vector storage.
    """

    @abstractmethod
    async def add(
        self,
        *,
        entry: MemoryEntry,
        embedding: list[float],
    ) -> None:
        """
        Store a memory entry together with its embedding.
        """
        raise NotImplementedError

    @abstractmethod
    async def add_many(
        self,
        *,
        entries: list[MemoryEntry],
        embeddings: list[list[float]],
    ) -> None:
        """
        Store multiple memory entries.
        """
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        *,
        embedding: list[float],
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Return the most similar memory entries.
        """
        raise NotImplementedError

    @abstractmethod
    async def remove(
        self,
        entry_id: str,
    ) -> None:
        """
        Remove a stored memory.
        """
        raise NotImplementedError

    @abstractmethod
    async def clear(
        self,
    ) -> None:
        """
        Remove all stored vectors.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
    ) -> int:
        """
        Return the number of stored vectors.
        """
        raise NotImplementedError

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return vector store diagnostics.
        """

        return {
            "store": type(self).__name__,
        }