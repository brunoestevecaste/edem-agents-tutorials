"""MCP-style tool wrappers for BigQuery operations."""

from __future__ import annotations

from src.project.services.bigquery_service import BigQueryService, QueryResult


class BigQueryMcpTools:
    """Teaching-friendly wrapper around BigQuery service operations."""

    def __init__(self, service: BigQueryService) -> None:
        self.service = service

    def list_tables(self) -> list[str]:
        """List available tables."""
        return self.service.list_tables()

    def get_table_schema(self, table_name: str) -> dict:
        """Get table schema metadata."""
        return self.service.get_table_schema(table_name)

    def run_read_only_query(self, sql: str) -> QueryResult:
        """Execute safe SQL query through the service abstraction."""
        return self.service.run_read_only_query(sql)
