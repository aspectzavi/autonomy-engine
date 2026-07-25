"""
Memory query.

Represents an immutable query against the memory subsystem.

MemoryQuery is intentionally backend-agnostic. Every memory provider,
whether vector, episodic, semantic, or persistent, accepts the same
query object.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    """
    Immutable memory query.
    """

    text: str

    limit: int = 10

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
        Whether the query contains metadata filters.
        """

        return bool(
            self.metadata,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def metadata_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a metadata filter.
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
        Return query diagnostics.
        """

        return {
            "text": self.text,
            "text_length": len(
                self.text,
            ),
            "limit": self.limit,
            "metadata_keys": tuple(
                sorted(
                    self.metadata.keys(),
                ),
            ),
        }