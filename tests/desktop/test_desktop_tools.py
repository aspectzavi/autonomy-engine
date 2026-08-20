"""
Desktop tool tests.

Each tool is tested for argument validation (missing/invalid
arguments fail cleanly) and correct delegation to the provider, using
a fake provider so no real window is needed.
"""

from __future__ import annotations

import pytest

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.tools.desktop.click_at_tool import ClickAtTool
from backend.tools.desktop.click_element_tool import ClickElementTool
from backend.tools.desktop.connect_window_tool import ConnectWindowTool
from backend.tools.desktop.drag_tool import DragTool
from backend.tools.desktop.extract_structured_tool import (
    ExtractStructuredTool,
)
from backend.tools.desktop.get_element_text_tool import (
    GetElementTextTool,
)
from backend.tools.desktop.launch_app_tool import LaunchAppTool
from backend.tools.desktop.list_windows_tool import ListWindowsTool
from backend.tools.desktop.move_mouse_tool import MoveMouseTool
from backend.tools.desktop.press_key_tool import PressKeyTool
from backend.tools.desktop.screenshot_tool import ScreenshotTool
from backend.tools.desktop.scroll_at_tool import ScrollAtTool
from backend.tools.desktop.type_into_element_tool import (
    TypeIntoElementTool,
)
from backend.tools.desktop.type_text_tool import TypeTextTool
from tests.desktop.fakes import FakeDesktopProvider


def _sessions() -> DesktopSessionManager:
    return DesktopSessionManager(provider=FakeDesktopProvider())


@pytest.mark.asyncio
async def test_list_windows_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ListWindowsTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert result.success
    assert sessions.provider.calls[0][0] == "list_windows"


@pytest.mark.asyncio
async def test_connect_window_requires_at_least_one_matcher() -> None:
    tool = ConnectWindowTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success


@pytest.mark.asyncio
async def test_connect_window_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ConnectWindowTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"title": "Notepad"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "connect_window"


@pytest.mark.asyncio
async def test_launch_app_requires_path() -> None:
    tool = LaunchAppTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success
    assert "path" in result.error


@pytest.mark.asyncio
async def test_launch_app_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = LaunchAppTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"path": "notepad.exe"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "launch"


@pytest.mark.asyncio
async def test_click_element_requires_a_matcher() -> None:
    tool = ClickElementTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success


@pytest.mark.asyncio
async def test_click_element_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ClickElementTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"automation_id": "submit"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "click_element"


@pytest.mark.asyncio
async def test_type_into_element_requires_text_and_matcher() -> None:
    tool = TypeIntoElementTool(sessions=_sessions())

    missing_text = await tool.execute(
        ToolContext(arguments={"name": "field"}),
    )
    assert not missing_text.success

    missing_matcher = await tool.execute(
        ToolContext(arguments={"text": "hello"}),
    )
    assert not missing_matcher.success


@pytest.mark.asyncio
async def test_type_into_element_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = TypeIntoElementTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={"control_type": "Document", "text": "hello"},
        ),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "type_into_element"


@pytest.mark.asyncio
async def test_get_element_text_requires_a_matcher() -> None:
    tool = GetElementTextTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success


@pytest.mark.asyncio
async def test_get_element_text_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = GetElementTextTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"name": "field"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "get_element_text"


@pytest.mark.asyncio
async def test_extract_structured_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ExtractStructuredTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert result.success
    assert sessions.provider.calls[0][0] == "extract_structured"


@pytest.mark.asyncio
async def test_click_at_requires_coordinates() -> None:
    tool = ClickAtTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={"x": 10}))

    assert not result.success


@pytest.mark.asyncio
async def test_click_at_rejects_non_numeric_coordinates() -> None:
    tool = ClickAtTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(arguments={"x": "far", "y": 10}),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_click_at_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ClickAtTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"x": 10, "y": 20}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "click_at"


@pytest.mark.asyncio
async def test_move_mouse_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = MoveMouseTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"x": 10, "y": 20}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "move_to"


@pytest.mark.asyncio
async def test_drag_requires_all_coordinates() -> None:
    tool = DragTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(arguments={"from_x": 0, "from_y": 0}),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_drag_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = DragTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "from_x": 0, "from_y": 0,
                "to_x": 10, "to_y": 10,
            },
        ),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "drag"


@pytest.mark.asyncio
async def test_scroll_at_requires_all_arguments() -> None:
    tool = ScrollAtTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(arguments={"x": 0, "y": 0}),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_scroll_at_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ScrollAtTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"x": 0, "y": 0, "amount": 5}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "scroll_at"


@pytest.mark.asyncio
async def test_type_text_requires_text() -> None:
    tool = TypeTextTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success


@pytest.mark.asyncio
async def test_type_text_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = TypeTextTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"text": "hello"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "type_text"


@pytest.mark.asyncio
async def test_press_key_requires_key() -> None:
    tool = PressKeyTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success


@pytest.mark.asyncio
async def test_press_key_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = PressKeyTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"key": "ctrl+s"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "press_key"


@pytest.mark.asyncio
async def test_screenshot_returns_base64_png() -> None:
    from backend.core.providers.provider_result import ProviderResult

    sessions = _sessions()
    sessions.provider.next_result = ProviderResult.ok(
        output=b"fake-png-bytes",
    )
    tool = ScreenshotTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert result.success
    assert result.output["format"] == "png"
    assert result.output["encoding"] == "base64"
    assert isinstance(result.output["data"], str)


@pytest.mark.asyncio
async def test_screenshot_propagates_provider_failure() -> None:
    from backend.core.providers.provider_result import ProviderResult

    sessions = _sessions()
    sessions.provider.next_result = ProviderResult.failure(
        "capture failed",
    )
    tool = ScreenshotTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success
    assert result.error == "capture failed"


@pytest.mark.asyncio
async def test_respects_cancellation() -> None:
    tool = ClickAtTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(
            arguments={"x": 1, "y": 1},
            cancelled=True,
        ),
    )

    assert not result.success
