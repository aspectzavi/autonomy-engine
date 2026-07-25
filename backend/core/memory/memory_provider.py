"""
Abstract memory provider.

Defines the contract implemented by all memory backends.

Memory providers are responsible for storing, retrieving,
and managing memory entries.

Examples:

- In-memory store
- Vector database
- Episodic memory
- Semantic memory
- Redis
- PostgreSQL
- ChromaDB
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.memory_result import MemoryResult


class MemoryProvider(ABC):
    """
    Abstract memory provider.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def start(
        self,
    ) -> None:
        """
        Initialize the provider.
        """

    @abstractmethod
    async def stop(
        self,
    ) -> None:
        """
        Shutdown the provider.
        """

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    @abstractmethod
    async def store(
        self,
        entry: MemoryEntry,
    ) -> None:
        """
        Store a memory entry.
        """

    @abstractmethod
    async def query(
        self,
        query: MemoryQuery,
    ) -> MemoryResult:
        """
        Execute a memory query.
        """

    @abstractmethod
    async def delete(
        self,
        entry_id: str,
    ) -> bool:
        """
        Delete a memory entry.

        Returns True if the entry existed.
        """

    @abstractmethod
    async def clear(
        self,
    ) -> None:
        """
        Remove all stored memories.
        """

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    @abstractmethod
    async def size(
        self,
    ) -> int:
        """
        Number of stored memories.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @abstractmethod
    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Provider diagnostics.
        """