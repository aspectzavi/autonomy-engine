"""
Lifecycle protocol.

Defines the common lifecycle contract implemented by kernel services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Lifecycle(ABC):
    """
    Abstract lifecycle contract.
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the component.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the component.
        """

    @abstractmethod
    async def restart(self) -> None:
        """
        Restart the component.
        """