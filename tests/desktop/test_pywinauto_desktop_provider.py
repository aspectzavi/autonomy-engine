"""
Pywinauto desktop provider integration tests.

Unlike the rest of tests/desktop/ (which use a fake provider for
speed), these launch a real Notepad window and drive it for real.
Slower, but they are what actually proves this backend works rather
than just type-checking against the DesktopProvider interface.
"""

from __future__ import annotations

import subprocess

import pytest

from backend.core.providers.desktop.pywinauto_desktop_provider import (
    PywinautoDesktopProvider,
)

pytestmark = pytest.mark.asyncio


def _kill_notepad() -> None:
    subprocess.run(
        ["taskkill", "/IM", "notepad.exe", "/F"],
        capture_output=True,
        check=False,
    )


@pytest.fixture(autouse=True)
def _cleanup_notepad():
    #
    # Clean up before AND after each test. Without the "before" pass,
    # a stray pre-existing Notepad window (the user's own, or left
    # over from a previous run) can confuse launch()'s before/after
    # window-diffing -- it isn't a bug in the diffing logic itself,
    # just a test-isolation requirement for it.
    #
    _kill_notepad()
    yield
    _kill_notepad()


async def test_launch_and_type_into_notepad() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()

        launch_result = await provider.launch(session, "notepad.exe")
        assert launch_result.success
        assert "Notepad" in launch_result.output[0]

        type_result = await provider.type_into_element(
            session,
            "hello from a real integration test",
            control_type="Document",
        )
        assert type_result.success

        title_result = await provider.current_window_title(session)
        assert title_result.success
        assert "Notepad" in title_result.output
    finally:
        await provider.stop()


async def test_extract_structured_against_a_real_window() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()
        await provider.launch(session, "notepad.exe")

        result = await provider.extract_structured(session)

        assert result.success
        data = result.output
        assert "Notepad" in data["window_title"]
        assert data["control_count"] > 0
        assert isinstance(data["controls"], list)
        assert all(
            {"control_type", "name", "automation_id", "rectangle"}
            <= control.keys()
            for control in data["controls"]
        )
    finally:
        await provider.stop()


async def test_screenshot_of_a_real_window_returns_valid_png_bytes() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()
        await provider.launch(session, "notepad.exe")

        result = await provider.screenshot(session)

        assert result.success
        #
        # PNG file signature.
        #
        assert result.output[:8] == b"\x89PNG\r\n\x1a\n"
    finally:
        await provider.stop()


async def test_list_windows_finds_the_launched_window() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()
        await provider.launch(session, "notepad.exe")

        result = await provider.list_windows(session)

        assert result.success
        titles = [window["title"] for window in result.output]
        assert any("Notepad" in title for title in titles)
    finally:
        await provider.stop()


async def test_connect_window_by_title_pattern() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session_a = await provider.create_session()
        await provider.launch(session_a, "notepad.exe")

        session_b = await provider.create_session()
        connect_result = await provider.connect_window(
            session_b,
            title_pattern=".*Notepad.*",
        )

        assert connect_result.success
    finally:
        await provider.stop()


async def test_click_element_and_press_key_on_a_real_window() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()
        await provider.launch(session, "notepad.exe")

        click_result = await provider.click_element(
            session,
            control_type="Document",
        )
        assert click_result.success

        type_result = await provider.type_text(session, "abc")
        assert type_result.success
    finally:
        await provider.stop()


async def test_launch_an_unknown_executable_fails_cleanly() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()

        result = await provider.launch(
            session, "this-executable-does-not-exist-xyz123.exe",
        )

        assert not result.success
    finally:
        await provider.stop()


async def test_acting_without_a_connected_window_fails_cleanly() -> None:
    provider = PywinautoDesktopProvider()

    try:
        session = await provider.create_session()

        result = await provider.click_element(
            session, control_type="Document",
        )

        assert not result.success
    finally:
        await provider.stop()


async def test_start_is_idempotent() -> None:
    provider = PywinautoDesktopProvider()

    try:
        await provider.start()
        assert provider.is_running

        await provider.start()
        assert provider.is_running
    finally:
        await provider.stop()
