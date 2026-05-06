"""Custom MCP server exposing BigQuery tools."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

from tools.bigquery_mcp_tools import BigQueryMcpTools


def create_server() -> Any:
    """Create and return a FastMCP server instance."""
    if importlib.util.find_spec("mcp.server") is None:
        raise RuntimeError("Install `mcp` package to run the demo MCP server.")

    mcp_module = importlib.import_module("mcp.server")
    fast_mcp_cls = getattr(mcp_module, "FastMCP")
    mcp = fast_mcp_cls(name="bigquery-mcp-server")
    tools = BigQueryMcpTools.from_settings()

    @mcp.tool()
    def list_tables() -> list[str]:
        """List tables in the configured BigQuery dataset."""
        return tools.list_tables()

    @mcp.tool()
    def get_table_schema(table_name: str) -> dict[str, Any]:
        """Return schema metadata for a table in the configured dataset."""
        return tools.get_table_schema(table_name)

    @mcp.tool()
    def run_read_only_query(sql: str) -> dict[str, Any]:
        """Run a guarded read-only SQL query."""
        return tools.run_read_only_query_json(sql)

    return mcp


def run() -> None:
    """Run MCP server if dependency is installed."""
    create_server().run()


if __name__ == "__main__":
    run()
