"""
Provider result.

Represents the outcome of provider execution.

Providers return ProviderResult instead of raising ordinary exceptions.
This keeps execution consistent across every provider implementation
(browser, filesystem, shell, python, vision, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class ProviderResult:
    """
    Immutable provider execution result.
    """

    success: bool

    output: object | None = None

    error: str | None = None

    started_at: datetime | None = None

    finished_at: datetime | None = None

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def ok(
        cls,
        *,
        output: object | None = None,
        started_at: datetime | None = None,
    ) -> ProviderResult:
        """
        Construct a successful provider result.
        """

        return cls(
            success=True,
            output=output,
            started_at=started_at,
            finished_at=datetime.now(UTC),
        )

    @classmethod
    def failure(
        cls,
        error: str,
        *,
        started_at: datetime | None = None,
    ) -> ProviderResult:
        """
        Construct a failed provider result.
        """

        return cls(
            success=False,
            error=error,
            started_at=started_at,
            finished_at=datetime.now(UTC),
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def failed(
        self,
    ) -> bool:
        """
        Whether execution failed.
        """

        return not self.success

    @property
    def duration_seconds(
        self,
    ) -> float | None:
        """
        Execution duration in seconds.
        """

        if (
            self.started_at is None
            or self.finished_at is None
        ):
            return None

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return provider diagnostics.
        """

        return {
            "success": self.success,
            "failed": self.failed,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
        }