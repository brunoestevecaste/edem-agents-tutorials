"""ADK agent with MCP tools from a local notes MCP server."""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    from model_config import get_model

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:9001/sse")

root_agent = Agent(
    model=get_model(),
    name="filesystem_agent",
    description="Manages simple text notes using MCP tools.",
    instruction=(
        "You are a notes assistant.\n"
        "Use create_note to save notes.\n"
        "Use list_notes to show available notes.\n"
        "Use read_note to read a specific note.\n"
        "Do not invent note content. Always use tools."
    ),
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=MCP_SERVER_URL,
                timeout=30,
            ),
            tool_filter=["create_note", "list_notes", "read_note"],
        ),
    ],
)
