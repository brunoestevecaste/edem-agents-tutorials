"""Tests for Talk with Data tools."""

import pytest

from services.bigquery_service import MockBigQueryService


def test_bigquery_service_exposes_schema() -> None:
    service = MockBigQueryService()
    schema = service.get_table_schema("orders")
    assert service.list_tables() == [
        "inventory_items",
        "order_items",
        "orders",
        "products",
        "users",
    ]
    assert {column["name"] for column in schema["columns"]} == {
        "order_id",
        "user_id",
        "status",
        "created_at",
    }


def test_bigquery_service_blocks_destructive_sql() -> None:
    service = MockBigQueryService()
    with pytest.raises(ValueError):
        service.run_read_only_query("DELETE FROM orders")


def test_bigquery_service_blocks_multi_statement_sql() -> None:
    service = MockBigQueryService()
    with pytest.raises(ValueError):
        service.run_read_only_query("SELECT * FROM orders; SELECT 1")
