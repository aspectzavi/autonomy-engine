"""
Runtime configuration.

Defines configuration for the kernel runtime.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RuntimeConfig:
    """
    Runtime execution configuration.
    """

    max_parallel_tasks: int = 32

    worker_threads: int = 8

    shutdown_timeout_seconds: int = 30

    startup_timeout_seconds: int = 30

    enable_diagnostics: bool = True

    enable_metrics: bool = True

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime configuration diagnostics.
        """
        return {
            "max_parallel_tasks": (
                self.max_parallel_tasks
            ),
            "worker_threads": (
                self.worker_threads
            ),
            "shutdown_timeout_seconds": (
                self.shutdown_timeout_seconds
            ),
            "startup_timeout_seconds": (
                self.startup_timeout_seconds
            ),
            "enable_diagnostics": (
                self.enable_diagnostics
            ),
            "enable_metrics": (
                self.enable_metrics
            ),
        }