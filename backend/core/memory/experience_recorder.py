"""
Experience recorder.

Converts completed agent executions into memory entries that can be
persisted by the runtime.

The recorder is intentionally independent of the runtime and memory
provider. It is responsible only for translating execution outcomes
into MemoryEntry objects.

Future versions may enrich recorded experiences with:

- capabilities used
- workflow identifier
- execution duration
- execution cost
- execution confidence
- tool usage
- semantic embeddings
- execution tags
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from uuid import uuid4

from backend.core.memory.memory_entry import MemoryEntry


class ExperienceRecorder:
    """
    Creates memory entries from execution outcomes.
    """

    # ------------------------------------------------------------------
    # Success
    # ------------------------------------------------------------------

    def record_success(
        self,
        *,
        goal: str,
        agent: str,
    ) -> MemoryEntry:
        """
        Create a memory entry describing a successful execution.
        """

        return MemoryEntry(
            id=str(
                uuid4(),
            ),
            content=(
                f"SUCCESS | "
                f"agent={agent} | "
                f"goal={goal}"
            ),
            metadata={
                "agent": agent,
                "goal": goal,
                "success": True,
                "timestamp": (
                    datetime.now(
                        UTC,
                    ).isoformat()
                ),
            },
        )

    # ------------------------------------------------------------------
    # Failure
    # ------------------------------------------------------------------

    def record_failure(
        self,
        *,
        goal: str,
        agent: str,
        error: str,
    ) -> MemoryEntry:
        """
        Create a memory entry describing a failed execution.
        """

        return MemoryEntry(
            id=str(
                uuid4(),
            ),
            content=(
                f"FAILURE | "
                f"agent={agent} | "
                f"goal={goal} | "
                f"error={error}"
            ),
            metadata={
                "agent": agent,
                "goal": goal,
                "success": False,
                "error": error,
                "timestamp": (
                    datetime.now(
                        UTC,
                    ).isoformat()
                ),
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return recorder diagnostics.
        """

        return {
            "component": "ExperienceRecorder",
        }