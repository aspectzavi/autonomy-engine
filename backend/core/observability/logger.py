"""
Kernel logging subsystem.

Provides centralized structured logging
for the runtime.
"""

from __future__ import annotations

import logging
from logging import Logger


class KernelLogger:
    """
    Central logging provider.

    Uses singleton behavior to guarantee
    one logging configuration across the engine.
    """

    _instance: KernelLogger | None = None

    def __new__(
        cls,
    ) -> KernelLogger:
        """
        Return singleton instance.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance._configure()

        return cls._instance

    def _configure(self) -> None:
        """
        Configure logging defaults.
        """

        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            ),
        )

    def get(
        self,
        name: str,
    ) -> Logger:
        """
        Return named logger.
        """

        return logging.getLogger(
            name,
        )