"""
Memory service.

Runtime-managed service responsible for coordinating memory access
throughout the autonomy engine.

The memory service provides a unified interface for:

- storing memories
- retrieving memories
- vector search
- episodic memory
- future long-term memory providers
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_store import MemoryStore
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.memory_result import MemoryResult


class MemoryService(KernelService):
    """
    Runtime service for autonomous memory.
    """

    def __init__(
        self,
        *,
        provider: MemoryStore,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="memory-service",
                version="1.0.0",
                description=(
                    "Coordinates runtime memory operations."
                ),
            ),
        )

        self._provider = provider

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> MemoryStore:
        """
        Runtime memory provider.
        """
        return self._provider

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def on_start(
        self,
    ) -> None:
        """
        Start memory infrastructure.
        """

    async def on_stop(
        self,
    ) -> None:
        """
        Stop memory infrastructure.
        """

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def store(
        self,
        entry: MemoryEntry,
    ) -> None:
        """
        Store a memory.
        """

        await self.provider.store(
            entry,
        )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def query(
        self,
        query: MemoryQuery,
    ) -> MemoryResult:
        """
        Search memory.
        """

        return await self.provider.query(
            query,
        )

    async def recall(
        self,
        query: MemoryQuery,
    ) -> MemoryResult:
        """
        Recall relevant memory.

        Alias for semantic search.
        """

        return await self.query(
            query,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return memory service diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "provider": (
                    self.provider.diagnostics()
                ),
            }
        )

        return diagnostics