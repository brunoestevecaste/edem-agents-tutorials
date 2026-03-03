"""Connect to a running MCP notes server and call its tools once."""

from __future__ import annotations

import os

import anyio
from mcp import ClientSession
from mcp.client.sse import sse_client


def _server_url() -> str:
    return os.getenv("MCP_SERVER_URL", "http://127.0.0.1:9001/sse")


def _print_tool_result(label: str, result) -> None:
    print(f"\n{label}")
    if getattr(result, "isError", False):
        print("Error")
        return

    for block in getattr(result, "content", []):
        text = getattr(block, "text", None)
        if text:
            print(text)


async def main() -> None:
    async with sse_client(_server_url()) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", ", ".join(tool.name for tool in tools.tools))

            create_result = await session.call_tool(
                "create_note",
                {"title": "tutorial_note", "content": "Hello from standalone MCP client."},
            )
            _print_tool_result("create_note", create_result)

            list_result = await session.call_tool("list_notes", {})
            _print_tool_result("list_notes", list_result)

            read_result = await session.call_tool("read_note", {"title": "tutorial_note"})
            _print_tool_result("read_note", read_result)


if __name__ == "__main__":
    anyio.run(main)
