from abc import ABC, abstractmethod


class Lifecycle(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Start the component."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop the component."""

    @abstractmethod
    async def restart(self) -> None:
        """Restart the component."""