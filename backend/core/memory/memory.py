"""
Memory facade.

Provides the primary interface used by the autonomy engine for storing
and retrieving memories.

The Memory class delegates all storage operations to a configured
MemoryProvider.

This keeps planners, agents, workflows, and capabilities independent of
the underlying storage implementation.
"""

from __future__ import annotations

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_provider import MemoryProvider
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.memory_result import MemoryResult
from backend.core.memory.memory_store import MemoryStore


class Memory:
    """
    High-level memory interface.
    """

    def __init__(
        self,
        *,
        provider: MemoryProvider | None = None,
    ) -> None:
        self._provider = (
            provider
            or MemoryStore()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> MemoryProvider:
        """
        Underlying memory provider.
        """

        return self._provider

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
    ) -> None:
        """
        Start the memory system.
        """

        await self.provider.start()

    async def stop(
        self,
    ) -> None:
        """
        Stop the memory system.
        """

        await self.provider.stop()

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def store(
        self,
        entry: MemoryEntry,
    ) -> None:
        """
        Store a memory entry.
        """

        await self.provider.store(
            entry,
        )

    async def query(
        self,
        query: MemoryQuery,
    ) -> MemoryResult:
        """
        Query memory.
        """

        return await self.provider.query(
            query,
        )

    async def delete(
        self,
        entry_id: str,
    ) -> bool:
        """
        Delete a memory entry.
        """

        return await self.provider.delete(
            entry_id,
        )

    async def clear(
        self,
    ) -> None:
        """
        Remove all memories.
        """

        await self.provider.clear()

    async def size(
        self,
    ) -> int:
        """
        Number of stored memories.
        """

        return await self.provider.size()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Memory diagnostics.
        """

        return {
            "provider": (
                self.provider.__class__.__name__
            ),
            "provider_diagnostics": (
                self.provider.diagnostics()
            ),
        }