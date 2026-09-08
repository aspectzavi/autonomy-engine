"""Submit one natural-language goal to the local autonomy engine."""

from __future__ import annotations

import asyncio
import json

import httpx


async def main() -> None:
    """Execute a browser goal through the HTTP API."""

    payload = {
        "agent": "planning",
        "description": "navigate the browser to a URL",
        "metadata": {
            "url": "https://jumia.com",
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/agents/execute",
            json=payload,
            timeout=None,
        )
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
