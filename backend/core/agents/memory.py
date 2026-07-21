"""
Agent memory.

Provides working memory for autonomous agents.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentMemory:
    """
    Mutable working memory for an agent.

    Stores arbitrary key/value pairs generated during execution.
    """

    _values: dict[str, Any] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a value from memory.
        """
        return self._values.get(key, default)

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value in memory.
        """
        self._values[key] = value

    def update(
        self,
        **values: Any,
    ) -> None:
        """
        Update multiple memory values.
        """
        self._values.update(values)

    def remove(
        self,
        key: str,
    ) -> Any:
        """
        Remove and return a value.

        Raises:
            KeyError:
                If the key does not exist.
        """
        return self._values.pop(key)

    def clear(self) -> None:
        """
        Clear all stored values.
        """
        self._values.clear()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Whether a key exists.
        """
        return key in self._values

    def keys(self) -> tuple[str, ...]:
        """
        Return all keys.
        """
        return tuple(self._values.keys())

    def values(self) -> tuple[Any, ...]:
        """
        Return all values.
        """
        return tuple(self._values.values())

    def items(self) -> tuple[tuple[str, Any], ...]:
        """
        Return all key/value pairs.
        """
        return tuple(self._values.items())

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return memory diagnostics.
        """
        return {
            "entries": len(self),
            "keys": sorted(self._values.keys()),
        }

    # ------------------------------------------------------------------
    # Dunder Methods
    # ------------------------------------------------------------------

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Whether a key exists.
        """
        return (
            isinstance(key, str)
            and key in self._values
        )

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Retrieve a value.
        """
        return self._values[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value.
        """
        self._values[key] = value

    def __delitem__(
        self,
        key: str,
    ) -> None:
        """
        Remove a value.
        """
        del self._values[key]

    def __len__(self) -> int:
        """
        Number of stored entries.
        """
        return len(self._values)

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over memory keys.
        """
        return iter(self._values)