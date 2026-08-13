"""
Memory result.

Represents the immutable result of a memory lookup.

Every memory provider returns a MemoryResult regardless of the
underlying storage implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.core.memory.memory_entry import MemoryEntry


@dataclass(frozen=True, slots=True)
class MemoryResult:
    """
    Immutable memory lookup result.
    """

    entries: tuple[MemoryEntry, ...] = ()

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def count(
        self,
    ) -> int:
        """
        Number of returned memory entries.
        """

        return len(
            self.entries,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether no memory entries were returned.
        """

        return not self.entries

    @property
    def has_results(
        self,
    ) -> bool:
        """
        Whether the query produced results.
        """

        return bool(
            self.entries,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def first(
        self,
    ) -> MemoryEntry | None:
        """
        Return the first memory entry.
        """

        if self.is_empty:
            return None

        return self.entries[0]

    def metadata_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve metadata.
        """

        return self.metadata.get(
            key,
            default,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return diagnostics.
        """

        return {
            "count": self.count,
            "is_empty": self.is_empty,
            "metadata_keys": tuple(
                sorted(
                    self.metadata.keys(),
                ),
            ),
        }