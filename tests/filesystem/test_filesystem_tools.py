"""
Filesystem tool tests.

Uses a real temporary directory as the sandboxed workspace for every
test -- these are genuine file I/O tests, not mocked, since the whole
point of this subsystem is the sandboxing behavior around real disk
access.
"""

from __future__ import annotations

import pytest

from backend.core.config.filesystem import FilesystemConfig
from backend.core.tools.context import ToolContext
from backend.tools.filesystem.append_file_tool import AppendFileTool
from backend.tools.filesystem.copy_file_tool import CopyFileTool
from backend.tools.filesystem.create_directory_tool import (
    CreateDirectoryTool,
)
from backend.tools.filesystem.delete_file_tool import DeleteFileTool
from backend.tools.filesystem.list_directory_tool import (
    ListDirectoryTool,
)
from backend.tools.filesystem.move_file_tool import MoveFileTool
from backend.tools.filesystem.read_file_tool import ReadFileTool
from backend.tools.filesystem.write_file_tool import WriteFileTool


@pytest.fixture
def config(tmp_path):
    return FilesystemConfig(
        workspace=tmp_path,
        create_missing_directories=True,
        overwrite_existing_files=True,
    )


@pytest.mark.asyncio
async def test_write_then_read_round_trip(config) -> None:
    write = WriteFileTool(config=config)
    read = ReadFileTool(config=config)

    write_result = await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "hello"}),
    )
    assert write_result.success
    assert write_result.output["encoding"] == "utf-8"

    read_result = await read.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    assert read_result.success
    assert read_result.output["content"] == "hello"


@pytest.mark.asyncio
async def test_write_respects_overwrite_disabled(tmp_path) -> None:
    strict_config = FilesystemConfig(
        workspace=tmp_path,
        overwrite_existing_files=False,
    )
    write = WriteFileTool(config=strict_config)

    first = await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "one"}),
    )
    assert first.success

    second = await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "two"}),
    )
    assert not second.success
    assert "already exists" in second.error


@pytest.mark.asyncio
async def test_write_requires_path_and_content(config) -> None:
    write = WriteFileTool(config=config)

    missing_path = await write.execute(
        ToolContext(arguments={"content": "x"}),
    )
    assert not missing_path.success

    missing_content = await write.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    assert not missing_content.success


@pytest.mark.asyncio
async def test_append_adds_to_existing_content(config) -> None:
    write = WriteFileTool(config=config)
    append = AppendFileTool(config=config)
    read = ReadFileTool(config=config)

    await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "one"}),
    )
    await append.execute(
        ToolContext(arguments={"path": "a.txt", "content": "two"}),
    )

    result = await read.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    assert result.output["content"] == "onetwo"


@pytest.mark.asyncio
async def test_append_creates_missing_directories(config) -> None:
    append = AppendFileTool(config=config)

    result = await append.execute(
        ToolContext(
            arguments={
                "path": "nested/dir/a.txt",
                "content": "x",
            },
        ),
    )

    assert result.success


@pytest.mark.asyncio
async def test_list_directory(config) -> None:
    write = WriteFileTool(config=config)
    create_dir = CreateDirectoryTool(config=config)
    list_dir = ListDirectoryTool(config=config)

    await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "x"}),
    )
    await create_dir.execute(
        ToolContext(arguments={"path": "sub"}),
    )

    result = await list_dir.execute(
        ToolContext(arguments={"path": "."}),
    )

    assert result.success
    assert result.output["count"] == 2
    names = {entry["name"] for entry in result.output["entries"]}
    assert names == {"a.txt", "sub"}


@pytest.mark.asyncio
async def test_list_directory_recursive(config) -> None:
    write = WriteFileTool(config=config)
    list_dir = ListDirectoryTool(config=config)

    await write.execute(
        ToolContext(
            arguments={"path": "sub/nested.txt", "content": "x"},
        ),
    )

    result = await list_dir.execute(
        ToolContext(arguments={"path": ".", "recursive": True}),
    )

    assert result.success
    paths = {entry["path"] for entry in result.output["entries"]}
    assert "sub" in paths
    assert any("nested.txt" in p for p in paths)


@pytest.mark.asyncio
async def test_create_directory_is_idempotent(config) -> None:
    create_dir = CreateDirectoryTool(config=config)

    first = await create_dir.execute(
        ToolContext(arguments={"path": "sub"}),
    )
    second = await create_dir.execute(
        ToolContext(arguments={"path": "sub"}),
    )

    assert first.success
    assert second.success


@pytest.mark.asyncio
async def test_delete_file(config) -> None:
    write = WriteFileTool(config=config)
    delete = DeleteFileTool(config=config)
    read = ReadFileTool(config=config)

    await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "x"}),
    )

    result = await delete.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    assert result.success

    after = await read.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    assert not after.success


@pytest.mark.asyncio
async def test_delete_missing_file_fails_cleanly(config) -> None:
    delete = DeleteFileTool(config=config)

    result = await delete.execute(
        ToolContext(arguments={"path": "does-not-exist.txt"}),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_copy_file(config) -> None:
    write = WriteFileTool(config=config)
    copy = CopyFileTool(config=config)
    read = ReadFileTool(config=config)

    await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "x"}),
    )

    result = await copy.execute(
        ToolContext(
            arguments={"source": "a.txt", "destination": "b.txt"},
        ),
    )
    assert result.success

    original = await read.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    copied = await read.execute(
        ToolContext(arguments={"path": "b.txt"}),
    )
    assert original.success and copied.success
    assert original.output["content"] == copied.output["content"]


@pytest.mark.asyncio
async def test_move_file(config) -> None:
    write = WriteFileTool(config=config)
    move = MoveFileTool(config=config)
    read = ReadFileTool(config=config)

    await write.execute(
        ToolContext(arguments={"path": "a.txt", "content": "x"}),
    )

    result = await move.execute(
        ToolContext(
            arguments={"source": "a.txt", "destination": "b.txt"},
        ),
    )
    assert result.success

    original = await read.execute(
        ToolContext(arguments={"path": "a.txt"}),
    )
    moved = await read.execute(
        ToolContext(arguments={"path": "b.txt"}),
    )
    assert not original.success
    assert moved.success

@pytest.mark.asyncio
async def test_absolute_path_outside_workspace_is_blocked(config) -> None:
    write = WriteFileTool(config=config)

    result = await write.execute(
        ToolContext(
            arguments={
                "path": "C:\\Windows\\System32\\evil.txt",
                "content": "x",
            },
        ),
    )

    assert not result.success
    assert "outside workspace" in result.error.lower() or (
        "not permitted" in result.error.lower()
    )


@pytest.mark.asyncio
async def test_path_traversal_outside_workspace_is_blocked(config) -> None:
    read = ReadFileTool(config=config)

    result = await read.execute(
        ToolContext(
            arguments={"path": "../../../../etc/passwd"},
        ),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_absolute_paths_allowed_when_configured(tmp_path) -> None:
    permissive = FilesystemConfig(
        workspace=tmp_path,
        allow_absolute_paths=True,
        create_missing_directories=True,
    )
    write = WriteFileTool(config=permissive)

    #
    # Still has to resolve inside the workspace even with absolute
    # paths allowed -- allow_absolute_paths permits the *form* of
    # the path, not escaping the sandbox.
    #
    inside_path = str(tmp_path / "a.txt")

    result = await write.execute(
        ToolContext(
            arguments={"path": inside_path, "content": "x"},
        ),
    )

    assert result.success


def test_config_registered_via_di_is_not_silently_reset() -> None:
    """
    Regression test for the DI auto-construction bug: FilesystemConfig
    is a concrete dataclass, so an *unregistered* FilesystemConfig
    dependency doesn't fail cleanly the way an unregistered ABC does --
    the container successfully auto-constructs one, but recursively
    "resolves" each primitive-typed field too, and bare str()/bool()
    succeed trivially, silently producing encoding='' and
    overwrite_existing_files=False instead of the dataclass's real
    defaults. This only verifies the dataclass itself still has sane
    defaults when constructed normally (not going through DI) --the
    DI-specific fix is registering a real instance in
    KernelBootstrap, covered by the live bootstrap smoke path.
    """

    plain_config = FilesystemConfig()

    assert plain_config.encoding == "utf-8"
    assert plain_config.overwrite_existing_files is False
    assert plain_config.create_missing_directories is False
