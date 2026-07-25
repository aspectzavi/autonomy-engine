"""
Provider metadata.

Describes a provider implementation.

Provider metadata identifies the provider itself rather than the
capabilities it implements.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    """
    Immutable provider metadata.
    """

    name: str

    version: str

    description: str = ""

    author: str = ""

    homepage: str = ""

    tags: frozenset[str] = field(
        default_factory=frozenset,
    )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def has_tag(
        self,
        tag: str,
    ) -> bool:
        """
        Determine whether this provider has a tag.
        """

        return tag in self.tags

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return provider metadata diagnostics.
        """

        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "tags": sorted(self.tags),
        }