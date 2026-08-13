"""
ExperienceRecorder tests.
"""

from __future__ import annotations

from backend.core.memory.experience_recorder import (
    ExperienceRecorder,
)


def test_record_success() -> None:
    """
    Successful executions should produce a success memory.
    """

    recorder = ExperienceRecorder()

    entry = recorder.record_success(
        goal="Search the web",
        agent="planning",
    )

    assert entry.metadata["success"] is True
    assert entry.metadata["agent"] == "planning"
    assert entry.metadata["goal"] == "Search the web"

    assert "SUCCESS" in entry.content
    assert "Search the web" in entry.content


def test_record_failure() -> None:
    """
    Failed executions should produce a failure memory.
    """

    recorder = ExperienceRecorder()

    entry = recorder.record_failure(
        goal="Open browser",
        agent="planning",
        error="Browser crashed",
    )

    assert entry.metadata["success"] is False
    assert entry.metadata["error"] == "Browser crashed"

    assert "FAILURE" in entry.content
    assert "Browser crashed" in entry.content


def test_success_and_failure_are_distinct() -> None:
    """
    Success and failure memories should differ.
    """

    recorder = ExperienceRecorder()

    success = recorder.record_success(
        goal="Task",
        agent="planning",
    )

    failure = recorder.record_failure(
        goal="Task",
        agent="planning",
        error="Failure",
    )

    assert success.content != failure.content
    assert success.metadata["success"] is True
    assert failure.metadata["success"] is False


def test_recorder_diagnostics() -> None:
    """
    Recorder diagnostics should identify the component.
    """

    recorder = ExperienceRecorder()

    diagnostics = recorder.diagnostics()

    assert diagnostics["component"] == "ExperienceRecorder"