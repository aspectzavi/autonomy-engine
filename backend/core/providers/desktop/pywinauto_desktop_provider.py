"""
Pywinauto desktop provider.

Concrete DesktopProvider implementation combining:

- pywinauto (Windows UI Automation) for structured element access --
  finding and interacting with controls by name/automation ID/control
  type, the desktop equivalent of a CSS selector. Deterministic, no
  LLM call per action.
- PyAutoGUI for coordinate-based mouse/keyboard control -- the
  fallback for apps (or parts of apps) with no accessible UI
  Automation tree: custom-rendered canvases, games, some legacy
  software.

pywinauto and pyautogui are both synchronous libraries; every call
here runs through asyncio.to_thread() so they don't block the event
loop.
"""

from __future__ import annotations

import asyncio
import io
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from backend.core.providers.desktop.desktop_config import (
    DesktopConfig,
)
from backend.core.providers.desktop.desktop_provider import (
    DesktopProvider,
)
from backend.core.providers.desktop.desktop_session import (
    DesktopSession,
)
from backend.core.providers.provider_metadata import (
    ProviderMetadata,
)
from backend.core.providers.provider_result import (
    ProviderResult,
)

if TYPE_CHECKING:
    from pywinauto.base_wrapper import BaseWrapper

_CAPABILITIES = frozenset(
    {
        "list_windows",
        "connect_window",
        "launch",
        "click_element",
        "type_into_element",
        "get_element_text",
        "extract_structured",
        "click_at",
        "move_to",
        "drag",
        "scroll_at",
        "type_text",
        "press_key",
        "screenshot",
        "current_window_title",
    },
)


class PywinautoDesktopProvider(DesktopProvider):
    """
    Desktop automation backed by pywinauto + PyAutoGUI.
    """

    def __init__(
        self,
        *,
        config: DesktopConfig | None = None,
    ) -> None:
        super().__init__(
            metadata=ProviderMetadata(
                name="pywinauto",
                version="1.0.0",
                description=(
                    "Desktop automation via pywinauto (structured "
                    "UI Automation) and PyAutoGUI (coordinate "
                    "fallback)."
                ),
                tags=frozenset(
                    {"desktop", "pywinauto", "pyautogui"},
                ),
            ),
        )

        self._config = (
            config
            if config is not None
            else DesktopConfig()
        )

        self._running = False

        #
        # Maps session.id -> the connected pywinauto window wrapper,
        # if any. A session with no entry here hasn't been connected
        # to a window yet (coordinate-based actions still work; the
        # structured element methods raise until connect_window() /
        # launch() is called).
        #
        self._windows: dict[str, "BaseWrapper"] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def config(
        self,
    ) -> DesktopConfig:
        """
        Active desktop configuration.
        """

        return self._config

    @property
    def is_running(
        self,
    ) -> bool:
        """
        Whether the provider has been started.
        """

        return self._running

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
    ) -> None:
        """
        Start the provider: configure PyAutoGUI's safety settings.

        Idempotent.
        """

        if self._running:
            return

        def _configure() -> None:
            import pyautogui

            pyautogui.FAILSAFE = self._config.failsafe
            pyautogui.PAUSE = self._config.action_pause

        await asyncio.to_thread(_configure)

        self._running = True

    async def stop(
        self,
    ) -> None:
        """
        Stop the provider.
        """

        self._windows.clear()
        self._running = False

    # ------------------------------------------------------------------
    # Session Management
    # ------------------------------------------------------------------

    async def create_session(
        self,
    ) -> DesktopSession:
        """
        Create a desktop session, not yet connected to any window.
        """

        await self.start()

        return DesktopSession()

    async def close_session(
        self,
        session: DesktopSession,
    ) -> None:
        """
        Close a desktop session.
        """

        self._windows.pop(session.id, None)
        session.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _window(
        self,
        session: DesktopSession,
    ) -> "BaseWrapper":
        window = self._windows.get(session.id)

        if window is None:
            raise ValueError(
                f"Session '{session.id}' is not connected to a "
                "window. Call connect_window() or launch() first.",
            )

        return window

    async def _run(
        self,
        action: Callable[[], Any],
    ) -> ProviderResult:
        """
        Run a blocking pywinauto/pyautogui action in a thread,
        converting exceptions into a ProviderResult instead of
        propagating them.
        """

        started_at = datetime.now(UTC)

        try:
            output = await asyncio.to_thread(action)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult.failure(
                str(exc),
                started_at=started_at,
            )

        return ProviderResult.ok(
            output=output,
            started_at=started_at,
        )

    # ------------------------------------------------------------------
    # Window / Application Management
    # ------------------------------------------------------------------

    async def list_windows(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        List currently open top-level windows.
        """

        def _list() -> list[dict[str, Any]]:
            from pywinauto import Desktop

            windows = Desktop(
                backend=self._config.backend,
            ).windows()

            results = []

            for window in windows:
                try:
                    title = window.window_text()

                    if not title:
                        continue

                    results.append(
                        {
                            "title": title,
                            "process_id": (
                                window.process_id()
                            ),
                            "class_name": (
                                window.friendly_class_name()
                            ),
                        },
                    )
                except Exception:  # noqa: BLE001, S112
                    continue

            return results

        return await self._run(_list)

    async def connect_window(
        self,
        session: DesktopSession,
        *,
        title: str | None = None,
        title_pattern: str | None = None,
        process_id: int | None = None,
    ) -> ProviderResult:
        """
        Connect the session to an already-open window.
        """

        if (
            title is None
            and title_pattern is None
            and process_id is None
        ):
            return ProviderResult.failure(
                "At least one of 'title', 'title_pattern', or "
                "'process_id' is required.",
            )

        def _connect() -> tuple[str, int | None]:
            from pywinauto import Desktop

            desktop = Desktop(
                backend=self._config.backend,
            )

            candidates = desktop.windows(
                title=title,
                title_re=title_pattern,
            )

            if process_id is not None:
                candidates = [
                    window
                    for window in candidates
                    if window.process_id() == process_id
                ]

            if not candidates:
                raise ValueError(
                    "No matching window found.",
                )

            window = candidates[0]

            self._windows[session.id] = window

            return (
                window.window_text(),
                window.process_id(),
            )

        result = await self._run(_connect)

        if result.success:
            window_title, pid = cast(
                "tuple[str, int | None]",
                result.output,
            )
            session.update(
                window_title=window_title,
                process_id=pid,
            )

        return result

    async def launch(
        self,
        session: DesktopSession,
        path: str,
        *,
        arguments: tuple[str, ...] = (),
    ) -> ProviderResult:
        """
        Launch a new process and connect the session to its window.
        """

        def _launch() -> tuple[str, int | None]:
            import time

            from pywinauto import Application, Desktop

            desktop = Desktop(
                backend=self._config.backend,
            )

            #
            # Match the new window by diffing window handles before
            # and after launch, rather than by matching the launched
            # process's own PID. Some apps (notably Windows 11's
            # packaged Notepad) launch through a shim/launcher
            # process whose PID never matches the actual window's
            # owning process, so PID matching alone misses the
            # window entirely.
            #
            before_handles = {
                window.handle
                for window in desktop.windows()
            }

            command = " ".join(
                (path, *arguments),
            ).strip()

            Application(
                backend=self._config.backend,
            ).start(command)

            deadline = (
                time.monotonic() + self._config.timeout
            )

            window = None

            while time.monotonic() < deadline:
                new_windows = [
                    candidate
                    for candidate in desktop.windows()
                    if candidate.handle not in before_handles
                ]

                titled = [
                    candidate
                    for candidate in new_windows
                    if candidate.window_text()
                ]

                if titled:
                    window = titled[0]
                    break

                if new_windows:
                    window = new_windows[0]
                    break

                time.sleep(0.2)

            if window is None:
                raise ValueError(
                    "Timed out waiting for a new window after "
                    f"launching '{path}'.",
                )

            self._windows[session.id] = window

            return (
                window.window_text(),
                window.process_id(),
            )

        result = await self._run(_launch)

        if result.success:
            window_title, pid = cast(
                "tuple[str, int | None]",
                result.output,
            )
            session.update(
                window_title=window_title,
                process_id=pid,
            )

        return result

    # ------------------------------------------------------------------
    # Structured element interaction
    # ------------------------------------------------------------------

    def _find(
        self,
        window: "BaseWrapper",
        *,
        name: str | None,
        automation_id: str | None,
        control_type: str | None,
    ) -> "BaseWrapper":
        if (
            name is None
            and automation_id is None
            and control_type is None
        ):
            raise ValueError(
                "At least one of 'name', 'automation_id', or "
                "'control_type' is required.",
            )

        candidates = (
            window.descendants(control_type=control_type)
            if control_type is not None
            else window.descendants()
        )

        for candidate in candidates:
            if (
                name is not None
                and candidate.window_text() != name
            ):
                continue

            if (
                automation_id is not None
                and candidate.automation_id() != automation_id
            ):
                continue

            return candidate

        raise ValueError(
            "No matching element found for "
            f"name={name!r}, automation_id={automation_id!r}, "
            f"control_type={control_type!r}.",
        )

    async def click_element(
        self,
        session: DesktopSession,
        *,
        name: str | None = None,
        automation_id: str | None = None,
        control_type: str | None = None,
    ) -> ProviderResult:
        """
        Click an element in the connected window.
        """

        def _click() -> None:
            window = self._window(session)
            element = self._find(
                window,
                name=name,
                automation_id=automation_id,
                control_type=control_type,
            )
            element.click_input()

        return await self._run(_click)

    async def type_into_element(
        self,
        session: DesktopSession,
        text: str,
        *,
        name: str | None = None,
        automation_id: str | None = None,
        control_type: str | None = None,
    ) -> ProviderResult:
        """
        Click an element and type text into it.
        """

        def _type() -> None:
            window = self._window(session)
            element = self._find(
                window,
                name=name,
                automation_id=automation_id,
                control_type=control_type,
            )
            element.click_input()
            element.type_keys(
                text,
                with_spaces=True,
            )

        return await self._run(_type)

    async def get_element_text(
        self,
        session: DesktopSession,
        *,
        name: str | None = None,
        automation_id: str | None = None,
        control_type: str | None = None,
    ) -> ProviderResult:
        """
        Retrieve the text of an element.
        """

        def _get() -> str:
            window = self._window(session)
            element = self._find(
                window,
                name=name,
                automation_id=automation_id,
                control_type=control_type,
            )
            return str(element.window_text())

        return await self._run(_get)

    async def extract_structured(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        Extract a generic structured summary of the connected
        window's UI tree.
        """

        def _extract() -> dict[str, Any]:
            window = self._window(session)

            controls = []

            for descendant in window.descendants():
                try:
                    rect = descendant.rectangle()

                    controls.append(
                        {
                            "control_type": (
                                descendant.element_info.control_type
                            ),
                            "name": descendant.window_text(),
                            "automation_id": (
                                descendant.automation_id()
                            ),
                            "rectangle": {
                                "left": rect.left,
                                "top": rect.top,
                                "right": rect.right,
                                "bottom": rect.bottom,
                            },
                        },
                    )
                except Exception:  # noqa: BLE001, S112
                    continue

            return {
                "window_title": window.window_text(),
                "control_count": len(controls),
                "controls": controls,
            }

        return await self._run(_extract)

    # ------------------------------------------------------------------
    # Coordinate-based fallback
    # ------------------------------------------------------------------

    async def click_at(
        self,
        session: DesktopSession,
        x: int,
        y: int,
        *,
        button: str = "left",
        clicks: int = 1,
    ) -> ProviderResult:
        """
        Click at absolute screen coordinates.
        """

        def _click() -> None:
            import pyautogui

            pyautogui.click(
                x=x,
                y=y,
                clicks=clicks,
                button=button,
            )

        return await self._run(_click)

    async def move_to(
        self,
        session: DesktopSession,
        x: int,
        y: int,
    ) -> ProviderResult:
        """
        Move the mouse to absolute screen coordinates.
        """

        def _move() -> None:
            import pyautogui

            pyautogui.moveTo(x, y)

        return await self._run(_move)

    async def drag(
        self,
        session: DesktopSession,
        *,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
    ) -> ProviderResult:
        """
        Drag the mouse from one point to another.
        """

        def _drag() -> None:
            import pyautogui

            pyautogui.moveTo(from_x, from_y)
            pyautogui.dragTo(
                to_x,
                to_y,
                duration=0.2,
                button="left",
            )

        return await self._run(_drag)

    async def scroll_at(
        self,
        session: DesktopSession,
        x: int,
        y: int,
        amount: int,
    ) -> ProviderResult:
        """
        Scroll at a screen position.
        """

        def _scroll() -> None:
            import pyautogui

            pyautogui.moveTo(x, y)
            pyautogui.scroll(amount)

        return await self._run(_scroll)

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    async def type_text(
        self,
        session: DesktopSession,
        text: str,
    ) -> ProviderResult:
        """
        Type text at the current keyboard focus.
        """

        def _type() -> None:
            import pyautogui

            pyautogui.write(text)

        return await self._run(_type)

    async def press_key(
        self,
        session: DesktopSession,
        key: str,
    ) -> ProviderResult:
        """
        Press a key or key combination (e.g. "enter", "ctrl+c").
        """

        def _press() -> None:
            import pyautogui

            keys = [
                part.strip().lower()
                for part in key.split("+")
                if part.strip()
            ]

            if not keys:
                raise ValueError("'key' must not be empty.")

            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)

        return await self._run(_press)

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    async def screenshot(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        Capture a screenshot: the connected window's region if a
        window is connected, otherwise the full screen.
        """

        def _capture() -> bytes:
            import pyautogui

            window = self._windows.get(session.id)

            region = None

            if window is not None:
                try:
                    rect = window.rectangle()
                    region = (
                        rect.left,
                        rect.top,
                        rect.width(),
                        rect.height(),
                    )
                except Exception:  # noqa: BLE001, S110
                    region = None

            image = pyautogui.screenshot(region=region)

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            return buffer.getvalue()

        return await self._run(_capture)

    async def current_window_title(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        Retrieve the connected window's current title.
        """

        def _title() -> str:
            window = self._window(session)
            return str(window.window_text())

        return await self._run(_title)

    # ------------------------------------------------------------------
    # Provider Interface
    # ------------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Determine whether this provider supports a capability.
        """

        return capability in _CAPABILITIES

    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> ProviderResult:
        """
        Execute a desktop capability by name.

        This is the generic entry point (matching the Provider
        contract); the typed methods above (click_element(),
        click_at(), ...) are the preferred way to call this provider
        directly.
        """

        if not self.supports(capability):
            return ProviderResult.failure(
                f"Unsupported desktop capability: '{capability}'.",
            )

        args = arguments or {}

        session = args.get("session")

        if not isinstance(session, DesktopSession):
            return ProviderResult.failure(
                "Missing required argument 'session'.",
            )

        if capability == "list_windows":
            return await self.list_windows(session)

        def _str_or_none(key: str) -> str | None:
            return cast("str | None", args.get(key))

        def _int(key: str, default: int = 0) -> int:
            return int(
                cast("str | int", args.get(key, default)),
            )

        if capability == "connect_window":
            raw_pid = cast(
                "int | None",
                args.get("process_id"),
            )

            return await self.connect_window(
                session,
                title=_str_or_none("title"),
                title_pattern=_str_or_none("title_pattern"),
                process_id=(
                    int(raw_pid)
                    if raw_pid is not None
                    else None
                ),
            )

        if capability == "launch":
            return await self.launch(
                session,
                str(args.get("path", "")),
                arguments=tuple(
                    cast(
                        "tuple[str, ...]",
                        args.get("arguments", ()),
                    ),
                ),
            )

        if capability == "click_element":
            return await self.click_element(
                session,
                name=_str_or_none("name"),
                automation_id=_str_or_none("automation_id"),
                control_type=_str_or_none("control_type"),
            )

        if capability == "type_into_element":
            return await self.type_into_element(
                session,
                str(args.get("text", "")),
                name=_str_or_none("name"),
                automation_id=_str_or_none("automation_id"),
                control_type=_str_or_none("control_type"),
            )

        if capability == "get_element_text":
            return await self.get_element_text(
                session,
                name=_str_or_none("name"),
                automation_id=_str_or_none("automation_id"),
                control_type=_str_or_none("control_type"),
            )

        if capability == "extract_structured":
            return await self.extract_structured(session)

        if capability == "click_at":
            return await self.click_at(
                session,
                _int("x"),
                _int("y"),
                button=str(args.get("button", "left")),
                clicks=_int("clicks", 1),
            )

        if capability == "move_to":
            return await self.move_to(
                session,
                _int("x"),
                _int("y"),
            )

        if capability == "drag":
            return await self.drag(
                session,
                from_x=_int("from_x"),
                from_y=_int("from_y"),
                to_x=_int("to_x"),
                to_y=_int("to_y"),
            )

        if capability == "scroll_at":
            return await self.scroll_at(
                session,
                _int("x"),
                _int("y"),
                _int("amount"),
            )

        if capability == "type_text":
            return await self.type_text(
                session,
                str(args.get("text", "")),
            )

        if capability == "press_key":
            return await self.press_key(
                session,
                str(args.get("key", "")),
            )

        if capability == "screenshot":
            return await self.screenshot(session)

        return await self.current_window_title(session)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return provider diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "is_running": self.is_running,
                "connected_windows": len(self._windows),
                "config": self._config.diagnostics(),
            },
        )

        return diagnostics
