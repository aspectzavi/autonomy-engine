"""
Framework-wide constants.

This module contains immutable constants shared throughout the
Autonomous AI Framework.

Only compile-time constants belong here.

Runtime configuration belongs in the Settings classes.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from pathlib import Path

################################################################################
# Framework Information
################################################################################

FRAMEWORK_NAME: str = "Autonomy Engine"

FRAMEWORK_SLUG: str = "autonomy-engine"

FRAMEWORK_VERSION: str = "0.1.0"

FRAMEWORK_AUTHOR: str = "Envisio"

FRAMEWORK_LICENSE: str = "MIT"

################################################################################
# Environment Variables
################################################################################

ENV_APP_ENV = "APP_ENV"

ENV_API_HOST = "API__HOST"

ENV_API_PORT = "API__PORT"

ENV_LOG_LEVEL = "LOGGING__LEVEL"

ENV_BROWSER_HEADLESS = "BROWSER__HEADLESS"

ENV_BROWSER_DEVTOOLS = "BROWSER__DEVTOOLS"

ENV_MEMORY_BACKEND = "MEMORY__BACKEND"

################################################################################
# Default Values
################################################################################

DEFAULT_HOST = "0.0.0.0"

DEFAULT_PORT = 8000

DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_ENCODING = "utf-8"

DEFAULT_TIMEZONE = "UTC"

################################################################################
# Browser
################################################################################

DEFAULT_BROWSER = "chromium"

DEFAULT_BROWSER_TIMEOUT = 30_000

DEFAULT_NAVIGATION_TIMEOUT = 60_000

DEFAULT_VIEWPORT_WIDTH = 1440

DEFAULT_VIEWPORT_HEIGHT = 900

################################################################################
# Retry
################################################################################

DEFAULT_RETRY_COUNT = 3

DEFAULT_BACKOFF_SECONDS = 2

################################################################################
# Directories
################################################################################

ROOT_DIRECTORY_NAME = "backend"

LOG_DIRECTORY_NAME = "logs"

DATA_DIRECTORY_NAME = "data"

SCREENSHOT_DIRECTORY_NAME = "screenshots"

VIDEO_DIRECTORY_NAME = "recordings"

ARTIFACT_DIRECTORY_NAME = "artifacts"

TEMP_DIRECTORY_NAME = "tmp"

################################################################################
# Logging
################################################################################

LOG_FILE_EXTENSION = ".jsonl"

TRACE_HEADER = "X-Trace-ID"

SESSION_HEADER = "X-Session-ID"

################################################################################
# FastAPI
################################################################################

OPENAPI_PATH = "/openapi.json"

DOCS_PATH = "/docs"

REDOC_PATH = "/redoc"

HEALTH_ENDPOINT = "/health"

################################################################################
# Planner
################################################################################

MAX_PLAN_DEPTH = 25

MAX_TASKS_PER_PLAN = 250

################################################################################
# Vision
################################################################################

OCR_LANGUAGE = "en"

################################################################################
# Plugins
################################################################################

PLUGIN_ENTRYPOINT = "register"

################################################################################
# Paths
################################################################################

PROJECT_ROOT = Path(__file__).resolve().parents[3]