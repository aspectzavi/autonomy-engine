#!/usr/bin/env python
"""
Autonomy Engine CLI.

Two ways to run the engine from the command line:

1. Direct tool invocation (recommended for real work -- scraping,
   file operations, browser/desktop automation). Predictable: calls
   exactly the tool you name, with exactly the arguments you give it.

       python run.py tool browser_scrape --args "{\"url\": \"https://www.jumia.co.ke/smartphones/\", \"max_pages\": 3}"
       python run.py tool write_file --args "{\"path\": \"out.txt\", \"content\": \"hello\"}"
       python run.py tool --list

2. Agent goal (experimental -- goes through reasoning, planning, and
   keyword-based capability matching before reaching a tool). Useful
   for testing the agent pipeline itself; less predictable than
   calling a tool directly, since the goal has to share real words
   with a tool's name/description to route correctly.

       python run.py goal "navigate browser to a URL" --meta "{\"url\": \"https://example.com\"}"

Output is JSON printed to stdout, so this composes with other tools
(pipe to `jq`, redirect to a file, etc.).

On Windows, JSON args are easiest to pass via --args-file / a file
rather than fighting cmd/PowerShell quote-escaping -- see the
--args-file examples in the README section below.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


async def _run_tool(name: str, args: dict[str, Any]) -> None:
    from backend.core.kernel.bootstrap import KernelBootstrap
    from backend.core.tools.context import ToolContext
    from backend.core.tools.exceptions import ToolNotFoundError

    bootstrap = KernelBootstrap()
    await bootstrap.runtime.start()

    try:
        try:
            tool = bootstrap.tool_service.registry.get(name)
        except ToolNotFoundError:
            available = sorted(
                t.name for t in bootstrap.tool_service.registry
            )
            _print_json(
                {
                    "success": False,
                    "error": f"Unknown tool '{name}'.",
                    "available_tools": available,
                },
            )
            sys.exit(1)

        result = await tool.execute(ToolContext(arguments=args))

        _print_json(
            {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "metadata": result.metadata,
            },
        )

        if not result.success:
            sys.exit(1)
    finally:
        await bootstrap.runtime.stop()


async def _list_tools() -> None:
    from backend.core.kernel.bootstrap import KernelBootstrap

    bootstrap = KernelBootstrap()
    await bootstrap.runtime.start()

    try:
        tools = sorted(
            bootstrap.tool_service.registry,
            key=lambda t: t.name,
        )
        _print_json(
            [
                {"name": t.name, "description": t.description}
                for t in tools
            ],
        )
    finally:
        await bootstrap.runtime.stop()


async def _run_goal(description: str, metadata: dict[str, Any]) -> None:
    from backend.core.agents.goal import Goal
    from backend.core.kernel.bootstrap import KernelBootstrap
    from backend.core.observability.events import EventBus
    from backend.core.observability.logger import KernelLogger
    from backend.core.tasks.context import TaskContext

    bootstrap = KernelBootstrap()
    await bootstrap.runtime.start()

    try:
        task_context = TaskContext(
            runtime=bootstrap.runtime_context,
            container=bootstrap.container,
            logger=KernelLogger(),
            events=EventBus(),
        )

        result = await bootstrap.agent_service.execute(
            agent="planning",
            goal=Goal(description=description, metadata=metadata),
            task_context=task_context,
        )

        _print_json(
            {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "duration_seconds": result.duration_seconds,
            },
        )

        if not result.success:
            sys.exit(1)
    finally:
        await bootstrap.runtime.stop()


def _parse_json_arg(raw: str | None, flag: str) -> dict[str, Any]:
    if raw is None:
        return {}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON for {flag}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(parsed, dict):
        print(f"{flag} must be a JSON object.", file=sys.stderr)
        sys.exit(2)

    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the autonomy engine from the command line.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    tool_parser = subparsers.add_parser(
        "tool",
        help="Call a specific tool directly.",
    )
    tool_parser.add_argument(
        "name",
        nargs="?",
        help="Tool name, e.g. browser_scrape.",
    )
    tool_parser.add_argument(
        "--args",
        help='Tool arguments as a JSON object, e.g. {"url": "..."}.',
    )
    tool_parser.add_argument(
        "--args-file",
        help="Path to a JSON file with tool arguments.",
    )
    tool_parser.add_argument(
        "--list",
        action="store_true",
        help="List every registered tool and exit.",
    )

    goal_parser = subparsers.add_parser(
        "goal",
        help="Submit a natural-language goal to the planning agent.",
    )
    goal_parser.add_argument(
        "description",
        help="The goal, in plain English.",
    )
    goal_parser.add_argument(
        "--meta",
        help=(
            "Goal metadata as a JSON object -- concrete arguments "
            "(e.g. url) for whatever tool the goal matches."
        ),
    )

    args = parser.parse_args()

    if args.command == "tool":
        if args.list:
            asyncio.run(_list_tools())
            return

        if not args.name:
            tool_parser.error("tool name is required (or use --list).")

        if args.args_file:
            with open(args.args_file, encoding="utf-8") as handle:
                tool_args = json.load(handle)
        else:
            tool_args = _parse_json_arg(args.args, "--args")

        asyncio.run(_run_tool(args.name, tool_args))
        return

    if args.command == "goal":
        metadata = _parse_json_arg(args.meta, "--meta")
        asyncio.run(_run_goal(args.description, metadata))
        return


if __name__ == "__main__":
    main()
