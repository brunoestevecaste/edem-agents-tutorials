"""MCP-style tool wrappers for BigQuery operations."""

from __future__ import annotations

import logging
from typing import Any

from config.settings import Settings, get_settings
from services.bigquery_service import (
    MockBigQueryService,
    RealBigQueryService,
)

logger = logging.getLogger(__name__)


class BigQueryMcpTools:
    """Teaching-friendly wrapper around BigQuery service operations."""

    def __init__(self, service: Any) -> None:
        self.service = service

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "BigQueryMcpTools":
        """Build tools from environment-backed settings."""
        settings = settings or get_settings()
        if settings.use_mock_services:
            logger.info(
                "[BigQuery mode] MOCK (USE_MOCK_SERVICES=true). "
                "Set USE_MOCK_SERVICES=false and GOOGLE_CLOUD_PROJECT to hit real BigQuery."
            )
            return cls(MockBigQueryService())
        logger.info(
            "[BigQuery mode] REAL (USE_MOCK_SERVICES=false) "
            "billing_project=%s dataset=%s.%s location=%s",
            settings.google_cloud_project,
            settings.bigquery_dataset_project,
            settings.bigquery_dataset,
            settings.bigquery_location,
        )
        return cls(
            RealBigQueryService(
                project_id=settings.google_cloud_project,
                dataset_project_id=settings.bigquery_dataset_project,
                dataset_id=settings.bigquery_dataset,
                allowed_tables=settings.bigquery_allowed_tables,
                location=settings.bigquery_location,
                max_bytes_billed=settings.bigquery_max_bytes_billed,
                query_timeout_seconds=settings.bigquery_query_timeout_seconds,
                max_result_rows=settings.bigquery_max_result_rows,
            )
        )

    def list_tables(self) -> list[str]:
        """List available tables."""
        return self.service.list_tables()

    def get_table_schema(self, table_name: str) -> dict:
        """Get table schema metadata."""
        return self.service.get_table_schema(table_name)

    def run_read_only_query(self, sql: str) -> Any:
        """Execute safe SQL query through the service abstraction."""
        return self.service.run_read_only_query(sql)

    def run_read_only_query_json(self, sql: str) -> dict[str, Any]:
        """Execute a safe query and return an MCP-friendly JSON object."""
        result = self.run_read_only_query(sql)
        return {
            "rows": result.rows,
            "sql": result.sql,
            "total_bytes_processed": result.total_bytes_processed,
        }
