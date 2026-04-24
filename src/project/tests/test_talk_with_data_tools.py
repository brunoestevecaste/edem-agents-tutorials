"""Tests for Talk with Data tools."""

import pytest

from src.project.services.bigquery_service import MockBigQueryService


def test_bigquery_service_exposes_schema() -> None:
    service = MockBigQueryService()
    schema = service.get_table_schema("sales_by_region")
    assert "sales_by_region" in service.list_tables()
    assert {column["name"] for column in schema["columns"]} == {
        "region",
        "quarter",
        "total_sales",
    }


def test_bigquery_service_blocks_destructive_sql() -> None:
    service = MockBigQueryService()
    with pytest.raises(ValueError):
        service.run_read_only_query("DELETE FROM sales_by_region")
