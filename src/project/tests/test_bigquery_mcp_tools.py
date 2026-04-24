"""Tests for BigQuery MCP-style tools."""

from services.bigquery_service import MockBigQueryService
from tools.bigquery_mcp_tools import BigQueryMcpTools


def test_bigquery_mcp_tool_returns_json_query_result() -> None:
    tools = BigQueryMcpTools(MockBigQueryService())
    result = tools.run_read_only_query_json("SELECT * FROM orders")
    assert result["rows"]
    assert result["sql"] == "SELECT * FROM orders"
    assert "total_bytes_processed" in result
