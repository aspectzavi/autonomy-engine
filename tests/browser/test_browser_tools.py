"""
Browser tool tests.

Each tool is tested for argument validation (missing/invalid
arguments fail cleanly) and correct delegation to the provider, using
a fake provider so no real browser is launched.
"""

from __future__ import annotations

import pytest

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.providers.provider_result import ProviderResult
from backend.core.tools.context import ToolContext
from backend.tools.browser.click_tool import ClickTool
from backend.tools.browser.download_tool import DownloadTool
from backend.tools.browser.extract_text_tool import ExtractTextTool
from backend.tools.browser.fill_tool import FillTool
from backend.tools.browser.navigate_tool import NavigateTool
from backend.tools.browser.press_key_tool import PressKeyTool
from backend.tools.browser.screenshot_tool import ScreenshotTool
from backend.tools.browser.scroll_tool import ScrollTool
from backend.tools.browser.upload_file_tool import UploadFileTool
from backend.tools.browser.wait_tool import WaitTool
from tests.browser.fakes import FakeBrowserProvider


def _sessions() -> BrowserSessionManager:
    return BrowserSessionManager(provider=FakeBrowserProvider())


@pytest.mark.asyncio
async def test_navigate_requires_url() -> None:
    tool = NavigateTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success
    assert "url" in result.error


@pytest.mark.asyncio
async def test_navigate_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = NavigateTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"url": "https://example.com"}),
    )

    assert result.success
    calls = sessions.provider.calls
    assert calls[0][0] == "navigate"
    assert calls[0][1][1] == "https://example.com"


@pytest.mark.asyncio
async def test_navigate_respects_cancellation() -> None:
    tool = NavigateTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(
            arguments={"url": "https://example.com"},
            cancelled=True,
        ),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_click_requires_selector() -> None:
    tool = ClickTool(sessions=_sessions())

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success
    assert "selector" in result.error


@pytest.mark.asyncio
async def test_click_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ClickTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"selector": "#submit"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "click"


@pytest.mark.asyncio
async def test_fill_requires_selector_and_text() -> None:
    tool = FillTool(sessions=_sessions())

    missing_selector = await tool.execute(
        ToolContext(arguments={"text": "hello"}),
    )
    assert not missing_selector.success

    missing_text = await tool.execute(
        ToolContext(arguments={"selector": "#name"}),
    )
    assert not missing_text.success


@pytest.mark.asyncio
async def test_fill_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = FillTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={"selector": "#name", "text": "hello"},
        ),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "type"


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
        ToolContext(arguments={"key": "Enter"}),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "press"


@pytest.mark.asyncio
async def test_scroll_defaults_to_zero() -> None:
    sessions = _sessions()
    tool = ScrollTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert result.success
    assert sessions.provider.calls[0][0] == "scroll"


@pytest.mark.asyncio
async def test_scroll_rejects_non_numeric_offsets() -> None:
    tool = ScrollTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(arguments={"x": "not-a-number"}),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_extract_text_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = ExtractTextTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert result.success
    assert sessions.provider.calls[0][0] == "text_content"


@pytest.mark.asyncio
async def test_screenshot_returns_base64_png() -> None:
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
    sessions = _sessions()
    sessions.provider.next_result = ProviderResult.failure(
        "capture failed",
    )
    tool = ScreenshotTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success
    assert result.error == "capture failed"


@pytest.mark.asyncio
async def test_wait_with_no_arguments_waits_default_timeout() -> None:
    sessions = _sessions()
    tool = WaitTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert result.success
    assert sessions.provider.calls[0][0] == "wait_for"


@pytest.mark.asyncio
async def test_wait_rejects_non_numeric_timeout() -> None:
    tool = WaitTool(sessions=_sessions())

    result = await tool.execute(
        ToolContext(arguments={"timeout_seconds": "soon"}),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_upload_file_requires_selector_and_path() -> None:
    tool = UploadFileTool(sessions=_sessions())

    missing_selector = await tool.execute(
        ToolContext(arguments={"file_path": "/tmp/a.txt"}),
    )
    assert not missing_selector.success

    missing_path = await tool.execute(
        ToolContext(arguments={"selector": "#file"}),
    )
    assert not missing_path.success


@pytest.mark.asyncio
async def test_upload_file_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = UploadFileTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "selector": "#file",
                "file_path": "/tmp/a.txt",
            },
        ),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "upload"


@pytest.mark.asyncio
async def test_download_requires_trigger_and_destination() -> None:
    tool = DownloadTool(sessions=_sessions())

    missing_trigger = await tool.execute(
        ToolContext(arguments={"destination": "/tmp/out.pdf"}),
    )
    assert not missing_trigger.success

    missing_destination = await tool.execute(
        ToolContext(arguments={"trigger_selector": "#dl"}),
    )
    assert not missing_destination.success


@pytest.mark.asyncio
async def test_download_delegates_to_provider() -> None:
    sessions = _sessions()
    tool = DownloadTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "trigger_selector": "#dl",
                "destination": "/tmp/out.pdf",
            },
        ),
    )

    assert result.success
    assert sessions.provider.calls[0][0] == "download"
