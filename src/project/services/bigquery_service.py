"""BigQuery service abstractions and mock behavior for local execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

BLOCKED_SQL_KEYWORDS = {"delete", "update", "insert", "drop", "truncate", "alter"}


@dataclass
class QueryResult:
    """Simple query result container."""

    rows: list[dict]
    sql: str


class BigQueryService(Protocol):
    """Interface for metadata browsing and read-only SQL execution."""

    def list_tables(self) -> list[str]:
        """List accessible tables."""

    def get_table_schema(self, table_name: str) -> dict:
        """Return schema for a table."""

    def run_read_only_query(self, sql: str) -> QueryResult:
        """Run read-only query and return rows."""


class MockBigQueryService:
    """In-memory BigQuery-like service for tutorial usage."""

    def __init__(self) -> None:
        self._tables = {
            "sales_by_region": [
                {"region": "EMEA", "quarter": "2026-Q1", "total_sales": 850000},
                {"region": "AMER", "quarter": "2026-Q1", "total_sales": 1350000},
                {"region": "APAC", "quarter": "2026-Q1", "total_sales": 970000},
            ]
        }

    def list_tables(self) -> list[str]:
        return sorted(self._tables.keys())

    def get_table_schema(self, table_name: str) -> dict:
        if table_name not in self._tables:
            return {"table": table_name, "columns": []}
        sample = self._tables[table_name][0]
        return {
            "table": table_name,
            "columns": [{"name": col, "type": type(val).__name__} for col, val in sample.items()],
        }

    def run_read_only_query(self, sql: str) -> QueryResult:
        lowered = sql.lower()
        if any(keyword in lowered for keyword in BLOCKED_SQL_KEYWORDS):
            raise ValueError("Destructive SQL operation blocked. Only read-only queries are allowed.")
        if "from sales_by_region" in lowered:
            return QueryResult(rows=self._tables["sales_by_region"], sql=sql)
        return QueryResult(rows=[], sql=sql)


class RealBigQueryService:
    """Placeholder for real BigQuery MCP-backed implementation."""

    def list_tables(self) -> list[str]:
        """TODO: Connect to MCP tool list_tables and return results."""
        raise NotImplementedError("Real BigQuery MCP integration is not implemented yet.")

    def get_table_schema(self, table_name: str) -> dict:
        """TODO: Connect to MCP tool get_table_schema and return results."""
        raise NotImplementedError("Real BigQuery MCP integration is not implemented yet.")

    def run_read_only_query(self, sql: str) -> QueryResult:
        """TODO: Connect to MCP tool run_read_only_query and return results."""
        raise NotImplementedError("Real BigQuery MCP integration is not implemented yet.")
