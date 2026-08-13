"""
Shared type aliases used throughout the Autonomous AI Framework.

This module centralizes commonly used type aliases to improve
readability, reduce duplication, and provide a single location
for evolving shared typing conventions.

The aliases defined here should remain lightweight and free of
runtime dependencies to avoid circular imports.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias
from uuid import UUID

# ---------------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------------

PathLike: TypeAlias = str | Path

# ---------------------------------------------------------------------------
# Generic JSON
# ---------------------------------------------------------------------------

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = (
    JsonPrimitive
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)
JsonDict: TypeAlias = dict[str, JsonValue]
JsonList: TypeAlias = list[JsonValue]

# ---------------------------------------------------------------------------
# Generic mappings
# ---------------------------------------------------------------------------

StringMap: TypeAlias = Mapping[str, Any]
MutableStringMap: TypeAlias = MutableMapping[str, Any]

# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

StringList: TypeAlias = list[str]
StringTuple: TypeAlias = tuple[str, ...]
AnySequence: TypeAlias = Sequence[Any]

# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

TraceId: TypeAlias = str
SessionId: TypeAlias = str
ExecutionId: TypeAlias = str
WorkflowId: TypeAlias = str
TaskId: TypeAlias = str
NodeId: TypeAlias = str
AgentId: TypeAlias = str
PluginId: TypeAlias = str
ArtifactId: TypeAlias = str
CorrelationId: TypeAlias = str

# ---------------------------------------------------------------------------
# UUID
# ---------------------------------------------------------------------------

UUIDLike: TypeAlias = UUID | str

# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

Milliseconds: TypeAlias = int
Seconds: TypeAlias = float

# ---------------------------------------------------------------------------
# Callables
# ---------------------------------------------------------------------------

SyncHandler: TypeAlias = Callable[..., Any]
AsyncHandler: TypeAlias = Callable[..., Awaitable[Any]]

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EnvironmentName: TypeAlias = str
LogLevel: TypeAlias = str

# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------

URL: TypeAlias = str
CSSSelector: TypeAlias = str
XPathSelector: TypeAlias = str

# ---------------------------------------------------------------------------
# Vision
# ---------------------------------------------------------------------------

BoundingBox: TypeAlias = tuple[int, int, int, int]

# ---------------------------------------------------------------------------
# Coordinates
# ---------------------------------------------------------------------------

Point2D: TypeAlias = tuple[int, int]
Size2D: TypeAlias = tuple[int, int]

# ---------------------------------------------------------------------------
# Binary
# ---------------------------------------------------------------------------

BytesLike: TypeAlias = bytes | bytearray

# ---------------------------------------------------------------------------
# Event payloads
# ---------------------------------------------------------------------------

EventPayload: TypeAlias = JsonDict

# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

Metadata: TypeAlias = dict[str, Any]

# ---------------------------------------------------------------------------
# Generic object
# ---------------------------------------------------------------------------

Serializable: TypeAlias = JsonValue | Mapping[str, Any]