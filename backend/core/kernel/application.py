"""
Kernel application.

The Application is the primary public interface to the kernel.

It provides a simple API for:

- registering services
- declaring dependencies
- starting the runtime
- stopping the runtime
- exposing diagnostics

The Application delegates construction to the KernelBootstrap and
execution to the Runtime.
"""

from __future__ import annotations

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.registry import ServiceRegistration
from backend.core.kernel.runtime import Runtime
from backend.core.kernel.runtime_state import RuntimeState
from backend.core.kernel.service import KernelService


class Application:
    """
    Kernel application.

    Public façade over the kernel runtime.
    """

    def __init__(self) -> None:
        self._bootstrap = KernelBootstrap()
        self._runtime: Runtime | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def runtime(self) -> Runtime:
        """
        Return the runtime.

        Raises:
            RuntimeError:
                If the application has not been built.
        """
        if self._runtime is None:
            raise RuntimeError(
                "Application has not been built."
            )

        return self._runtime

    @property
    def state(self) -> RuntimeState:
        """
        Current runtime state.
        """
        if self._runtime is None:
            return RuntimeState.CREATED

        return self._runtime.state

    @property
    def is_running(self) -> bool:
        """
        Whether the application is running.
        """
        return self._runtime is not None and self._runtime.is_running

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        registration: ServiceRegistration,
    ) -> "Application":
        """
        Register a service registration.
        """
        self._bootstrap.register(registration)
        return self

    def register_service(
        self,
        service: KernelService,
    ) -> "Application":
        """
        Register a service instance.
        """
        self._bootstrap.register_service(service)
        return self

    def depends_on(
        self,
        service: str,
        *dependencies: str,
    ) -> "Application":
        """
        Declare service dependencies.
        """
        self._bootstrap.depends_on(
            service,
            *dependencies,
        )
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> "Application":
        """
        Build the runtime.

        Safe to call multiple times.
        """
        if self._runtime is None:
            self._runtime = self._bootstrap.build()

        return self

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """
        Build and start the application.
        """
        self.build()
        await self.runtime.start()

    async def stop(self) -> None:
        """
        Stop the application.
        """
        if self._runtime is None:
            return

        await self.runtime.stop()

    async def restart(self) -> None:
        """
        Restart the application.
        """
        self.build()
        await self.runtime.restart()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return application diagnostics.
        """
        if self._runtime is None:
            return {
                "state": RuntimeState.CREATED.value,
                "built": False,
            }

        return {
            "built": True,
            "state": self.runtime.state.value,
            "runtime": self.runtime.diagnostics(),
        }