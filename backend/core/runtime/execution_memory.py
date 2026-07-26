"""
Execution memory.

Represents the working memory attached to a single execution session.

ExecutionMemory is intentionally separate from MemoryService.

MemoryService provides persistent storage.

ExecutionMemory provides temporary in-memory state for a running
execution, allowing agents to accumulate retrieved memories,
new observations, and generated memories before optionally persisting
them.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_result import MemoryResult


@dataclass(slots=True)
class ExecutionMemory:
    """
    Working memory for a single execution.
    """

    #
    # Retrieved memories from long-term storage.
    #
    retrieved: MemoryResult | None = None

    #
    # Memories created during execution.
    #
    generated: list[MemoryEntry] = field(
        default_factory=list,
    )

    #
    # Scratchpad values used by agents.
    #
    variables: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Retrieved memory
    # ------------------------------------------------------------------

    def attach(
        self,
        result: MemoryResult,
    ) -> None:
        """
        Attach retrieved memory.
        """
        self.retrieved = result

    # ------------------------------------------------------------------
    # Generated memory
    # ------------------------------------------------------------------

    def remember(
        self,
        entry: MemoryEntry,
    ) -> None:
        """
        Queue a generated memory.

        Persistence is handled later by MemoryService.
        """
        self.generated.append(entry)

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a variable.
        """
        return self.variables.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store a variable.
        """
        self.variables[key] = value

    def clear_variables(
        self,
    ) -> None:
        """
        Remove all temporary variables.
        """
        self.variables.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution memory diagnostics.
        """

        return {
            "retrieved": (
                0
                if self.retrieved is None
                else len(self.retrieved.entries)
            ),
            "generated": len(
                self.generated,
            ),
            "variables": len(
                self.variables,
            ),
        }