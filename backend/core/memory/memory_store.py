"""
In-memory memory store.

Provides a concrete implementation of MemoryProvider using an
in-memory dictionary.

This implementation is intended as the foundation for more advanced
memory systems such as vector memory and episodic memory.
"""

from __future__ import annotations

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_provider import MemoryProvider
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.memory_result import MemoryResult


class MemoryStore(MemoryProvider):
    """
    In-memory memory provider.
    """

    def __init__(
        self,
    ) -> None:
        self._entries: dict[str, MemoryEntry] = {}
        self._running = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_running(
        self,
    ) -> bool:
        """
        Whether the store is active.
        """

        return self._running

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
    ) -> None:
        """
        Start the memory store.
        """

        self._running = True

    async def stop(
        self,
    ) -> None:
        """
        Stop the memory store.
        """

        self._running = False

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

        self._entries[
            entry.id
        ] = entry

    async def query(
        self,
        query: MemoryQuery,
    ) -> MemoryResult:
        """
        Execute a memory query.

        Current implementation performs a simple substring search.
        """

        text = query.text.casefold()

        matches = [
            entry
            for entry in self._entries.values()
            if text
            in entry.content.casefold()
        ]

        return MemoryResult(
            entries=tuple(
                matches[
                    : query.limit
                ]
            ),
        )

    async def delete(
        self,
        entry_id: str,
    ) -> bool:
        """
        Delete a memory entry.
        """

        return (
            self._entries.pop(
                entry_id,
                None,
            )
            is not None
        )

    async def clear(
        self,
    ) -> None:
        """
        Remove every memory entry.
        """

        self._entries.clear()

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    async def size(
        self,
    ) -> int:
        """
        Number of stored memories.
        """

        return len(
            self._entries,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Memory store diagnostics.
        """

        return {
            "running": self.is_running,
            "entries": len(
                self._entries,
            ),
        }