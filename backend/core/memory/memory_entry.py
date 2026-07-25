"""
Memory entry.

Represents a single immutable memory stored by the autonomy engine.

Memory entries are the fundamental unit of storage for all memory
implementations, including vector memory, episodic memory, semantic
memory, and future persistent memory providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """
    Immutable memory record.
    """

    id: str

    content: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def has_metadata(
        self,
    ) -> bool:
        """
        Whether the memory contains metadata.
        """

        return bool(self.metadata)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def metadata_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a metadata value.
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
        Return diagnostics for the memory entry.
        """

        return {
            "id": self.id,
            "content_length": len(self.content),
            "created_at": self.created_at.isoformat(),
            "metadata_keys": tuple(
                sorted(self.metadata.keys()),
            ),
        }