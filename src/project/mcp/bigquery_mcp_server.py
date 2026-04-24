"""Simple custom MCP server example for BigQuery-like tools.

This server intentionally uses in-memory mock data so students can run locally.
"""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

MOCK_TABLES = {
    "sales_by_region": [
        {"region": "EMEA", "quarter": "2026-Q1", "total_sales": 850000},
        {"region": "AMER", "quarter": "2026-Q1", "total_sales": 1350000},
        {"region": "APAC", "quarter": "2026-Q1", "total_sales": 970000},
    ]
}
BLOCKED = {"delete", "update", "insert", "drop", "truncate", "alter"}


def create_server() -> Any:
    """Create and return a FastMCP server instance."""
    if importlib.util.find_spec("mcp.server") is None:
        raise RuntimeError("Install `mcp` package to run the demo MCP server.")

    mcp_module = importlib.import_module("mcp.server")
    fast_mcp_cls = getattr(mcp_module, "FastMCP")
    mcp = fast_mcp_cls(name="simple-bigquery-mcp-server")

    @mcp.tool()
    def list_tables() -> list[str]:
        """List available mock tables."""
        return sorted(MOCK_TABLES.keys())

    @mcp.tool()
    def get_table_schema(table_name: str) -> dict[str, Any]:
        """Return schema for a given mock table."""
        rows = MOCK_TABLES.get(table_name, [])
        if not rows:
            return {"table": table_name, "columns": []}
        first_row = rows[0]
        return {
            "table": table_name,
            "columns": [{"name": key, "type": type(value).__name__} for key, value in first_row.items()],
        }

    @mcp.tool()
    def run_read_only_query(sql: str) -> dict[str, Any]:
        """Execute a simple read-only query simulation."""
        lowered = sql.lower()
        if any(keyword in lowered for keyword in BLOCKED):
            return {"error": "Destructive SQL blocked."}
        if "from sales_by_region" in lowered:
            return {"rows": MOCK_TABLES["sales_by_region"], "sql": sql}
        return {"rows": [], "sql": sql}

    return mcp


def run() -> None:
    """Run MCP server if dependency is installed."""
    create_server().run()


if __name__ == "__main__":
    run()
