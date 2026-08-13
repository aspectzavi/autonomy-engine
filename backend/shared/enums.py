"""
Shared framework enumerations.

This module contains globally shared enumerations used throughout the
Autonomous AI Framework. Keeping enums centralized prevents duplicated
string literals and ensures consistency across agents, services,
configuration, logging, events, and orchestration.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum


# ============================================================================
# Environment
# ============================================================================


class Environment(StrEnum):
    """Application runtime environment."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# ============================================================================
# Execution
# ============================================================================


class ExecutionStatus(StrEnum):
    """Overall execution status."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskStatus(StrEnum):
    """Planner task status."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================================
# Agents
# ============================================================================


class AgentType(StrEnum):
    """Supported framework agents."""

    PLANNER = "planner"
    BROWSER = "browser"
    DESKTOP = "desktop"
    VISION = "vision"
    MEMORY = "memory"
    REVIEWER = "reviewer"


class AgentState(StrEnum):
    """Current agent lifecycle state."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


# ============================================================================
# Browser
# ============================================================================


class BrowserState(StrEnum):
    """Browser lifecycle."""

    CLOSED = "closed"
    STARTING = "starting"
    READY = "ready"
    NAVIGATING = "navigating"
    LOADING = "loading"
    IDLE = "idle"
    ERROR = "error"


class BrowserEngine(StrEnum):
    """Supported browser engines."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


# ============================================================================
# Desktop
# ============================================================================


class WindowState(StrEnum):
    """Desktop window state."""

    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"


# ============================================================================
# Memory
# ============================================================================


class MemoryScope(StrEnum):
    """Memory persistence scope."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SESSION = "session"


# ============================================================================
# Plugins
# ============================================================================


class PluginState(StrEnum):
    """Plugin lifecycle."""

    DISCOVERED = "discovered"
    REGISTERED = "registered"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"


# ============================================================================
# Events
# ============================================================================


class EventType(StrEnum):
    """Framework event categories."""

    COMMAND = "command"
    GRAPH = "graph"
    AGENT = "agent"
    BROWSER = "browser"
    DESKTOP = "desktop"
    MEMORY = "memory"
    REVIEWER = "reviewer"
    SYSTEM = "system"
    ERROR = "error"


# ============================================================================
# Logging
# ============================================================================


class LogLevel(StrEnum):
    """Supported log levels."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================================
# Telemetry
# ============================================================================


class SpanStatus(StrEnum):
    """Tracing span status."""

    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"


# ============================================================================
# API
# ============================================================================


class HttpMethod(StrEnum):
    """Supported HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


# ============================================================================
# Retry
# ============================================================================


class RetryStrategy(StrEnum):
    """Retry algorithms."""

    NONE = "none"
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


# ============================================================================
# Priority
# ============================================================================


class Priority(IntEnum):
    """Execution priority."""

    LOW = 10
    NORMAL = 50
    HIGH = 75
    CRITICAL = 100


# ============================================================================
# Result
# ============================================================================


class ResultType(StrEnum):
    """Execution result."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


# ============================================================================
# Artifact
# ============================================================================


class ArtifactType(StrEnum):
    """Generated execution artifacts."""

    SCREENSHOT = "screenshot"
    VIDEO = "video"
    TRACE = "trace"
    LOG = "log"
    REPORT = "report"
    DOWNLOAD = "download"


# ============================================================================
# Security
# ============================================================================


class SecretSource(StrEnum):
    """Configuration secret source."""

    ENVIRONMENT = "environment"
    DOTENV = "dotenv"
    FILE = "file"
    VAULT = "vault"


# ============================================================================
# Base Enum
# ============================================================================


class AutoNameEnum(StrEnum):
    """
    Base class for future enums that should automatically use the member
    name as its value.
    """

    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,
        count: int,
        last_values: list[str],
    ) -> str:
        return name.lower()