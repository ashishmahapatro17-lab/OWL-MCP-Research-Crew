"""MCP stdio client for the local DuckDuckGo search server."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).resolve().parent.parent / "mcp_server" / "search_server.py"


async def search_with_mcp(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Launch the MCP server, call search_web, and normalize its result."""
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        env=None,
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            if not any(tool.name == "search_web" for tool in tools.tools):
                raise RuntimeError("MCP server did not expose the search_web tool.")

            response = await session.call_tool(
                "search_web",
                {"query": query, "max_results": max_results},
            )
            if getattr(response, "isError", False):
                raise RuntimeError("The MCP search tool reported an error.")

            # The server returns JSON as text so the client remains independent
            # of any particular search-provider response schema.
            import json

            for block in response.content:
                text = getattr(block, "text", None)
                if text:
                    payload = json.loads(text)
                    return payload.get("results", [])
    return []
