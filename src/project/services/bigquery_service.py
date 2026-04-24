"""BigQuery service abstractions and implementations."""

from __future__ import annotations

import datetime as dt
import decimal
import logging
import re
from dataclasses import dataclass
from typing import Any

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

logger = logging.getLogger(__name__)

BLOCKED_SQL_KEYWORDS = {
    "alter",
    "call",
    "create",
    "delete",
    "drop",
    "execute",
    "export",
    "grant",
    "insert",
    "load",
    "merge",
    "revoke",
    "truncate",
    "update",
}
TABLE_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass
class QueryResult:
    """Simple query result container."""

    rows: list[dict[str, Any]]
    sql: str
    total_bytes_processed: int | None = None


def validate_read_only_sql(sql: str) -> str:
    """Reject obvious non-read-only SQL before sending it to BigQuery."""
    cleaned = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    cleaned = re.sub(r"--.*?$", " ", cleaned, flags=re.MULTILINE).strip()
    cleaned = cleaned[:-1].strip() if cleaned.endswith(";") else cleaned
    if not cleaned:
        raise ValueError("SQL cannot be empty.")
    if ";" in cleaned:
        raise ValueError("Only one SQL statement is allowed.")
    first_word = cleaned.split(None, 1)[0].lower()
    if first_word not in {"select", "with"}:
        raise ValueError("Only read-only SELECT queries are allowed.")
    for keyword in BLOCKED_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", cleaned, flags=re.IGNORECASE):
            raise ValueError("Destructive or administrative SQL is blocked.")
    return cleaned


def _json_safe(value: Any) -> Any:
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (dt.date, dt.datetime, dt.time)):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


class MockBigQueryService:
    """In-memory BigQuery-like service for tutorial usage."""

    def __init__(self) -> None:
        self._tables = {
            "users": [{"id": 1, "country": "USA", "age": 34, "traffic_source": "Search"}],
            "orders": [{"order_id": 101, "user_id": 1, "status": "Shipped", "created_at": "2024-01-15"}],
            "order_items": [{"order_id": 101, "product_id": 501, "sale_price": 89.99, "status": "Shipped"}],
            "products": [{"id": 501, "category": "Outerwear", "name": "Wool Coat", "cost": 42.50}],
            "inventory_items": [{"product_id": 501, "sold_at": None, "cost": 42.50}],
        }

    def list_tables(self) -> list[str]:
        logger.info("[MOCK BigQuery] list_tables()")
        return sorted(self._tables.keys())

    def get_table_schema(self, table_name: str) -> dict[str, Any]:
        logger.info("[MOCK BigQuery] get_table_schema(table_name=%s)", table_name)
        if table_name not in self._tables:
            return {"table": table_name, "columns": []}
        sample = self._tables[table_name][0]
        return {
            "table": table_name,
            "columns": [{"name": col, "type": type(val).__name__} for col, val in sample.items()],
        }

    def run_read_only_query(self, sql: str) -> QueryResult:
        cleaned = validate_read_only_sql(sql)
        logger.info("[MOCK BigQuery] run_read_only_query sql=%s", cleaned)
        lowered = cleaned.lower()
        for table_name, rows in self._tables.items():
            if f"from {table_name}" in lowered or f"thelook_ecommerce.{table_name}" in lowered:
                return QueryResult(rows=rows, sql=cleaned)
        return QueryResult(rows=[], sql=cleaned)


class RealBigQueryService:
    """BigQuery-backed service using Application Default Credentials."""

    def __init__(
        self,
        project_id: str,
        dataset_project_id: str,
        dataset_id: str,
        allowed_tables: list[str],
        location: str = "US",
        max_bytes_billed: int = 1_000_000_000,
        query_timeout_seconds: int = 30,
        max_result_rows: int = 100,
        client: Any | None = None,
    ) -> None:
        if bigquery is None:
            raise RuntimeError("Install `google-cloud-bigquery` to use RealBigQueryService.")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT is required for RealBigQueryService.")
        if not PROJECT_ID_RE.fullmatch(dataset_project_id):
            raise ValueError("BIGQUERY_DATASET_PROJECT must be a valid project id.")
        if not TABLE_ID_RE.fullmatch(dataset_id):
            raise ValueError("BIGQUERY_DATASET must be a simple dataset id.")

        self.project_id = project_id
        self.dataset_project_id = dataset_project_id
        self.dataset_id = dataset_id
        self.allowed_tables = set(allowed_tables)
        self.location = location
        self.max_bytes_billed = max_bytes_billed
        self.query_timeout_seconds = query_timeout_seconds
        self.max_result_rows = max_result_rows
        self.client = client or bigquery.Client(project=project_id, location=location)
        self.default_dataset = bigquery.DatasetReference(dataset_project_id, dataset_id)
        logger.info(
            "[REAL BigQuery] client initialized billing_project=%s dataset=%s.%s location=%s "
            "max_bytes_billed=%d max_result_rows=%d",
            project_id,
            dataset_project_id,
            dataset_id,
            location,
            max_bytes_billed,
            max_result_rows,
        )

    def list_tables(self) -> list[str]:
        logger.info(
            "[REAL BigQuery] list_tables dataset=%s.%s",
            self.dataset_project_id,
            self.dataset_id,
        )
        tables = self.client.list_tables(self.default_dataset)
        return sorted(table.table_id for table in tables if table.table_id in self.allowed_tables)

    def get_table_schema(self, table_name: str) -> dict[str, Any]:
        logger.info(
            "[REAL BigQuery] get_table_schema table=%s.%s.%s",
            self.dataset_project_id,
            self.dataset_id,
            table_name,
        )
        table = self.client.get_table(self._table_ref(table_name))
        return {
            "table": table.table_id,
            "full_name": f"{table.project}.{table.dataset_id}.{table.table_id}",
            "columns": [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or "",
                }
                for field in table.schema
            ],
        }

    def run_read_only_query(self, sql: str) -> QueryResult:
        cleaned = validate_read_only_sql(sql)
        logger.info("[REAL BigQuery] dry_run sql=%s", cleaned)
        dry_run_config = bigquery.QueryJobConfig(
            default_dataset=self.default_dataset,
            dry_run=True,
            maximum_bytes_billed=self.max_bytes_billed,
            use_legacy_sql=False,
            use_query_cache=False,
        )
        dry_run = self.client.query(cleaned, job_config=dry_run_config, location=self.location)
        logger.info(
            "[REAL BigQuery] dry_run ok bytes_processed=%s referenced_tables=%s",
            dry_run.total_bytes_processed,
            [f"{t.project}.{t.dataset_id}.{t.table_id}" for t in (dry_run.referenced_tables or [])],
        )
        for table in dry_run.referenced_tables or []:
            if table.project != self.dataset_project_id or table.dataset_id != self.dataset_id:
                raise ValueError("Query may only reference tables in the configured dataset.")
            if table.table_id not in self.allowed_tables:
                raise ValueError("Query may only reference allowed TheLook tables.")

        job_config = bigquery.QueryJobConfig(
            default_dataset=self.default_dataset,
            maximum_bytes_billed=self.max_bytes_billed,
            use_legacy_sql=False,
            labels={"app": "agents-tutorials", "component": "talk-with-data"},
        )
        logger.info("[REAL BigQuery] executing query job")
        query_job = self.client.query(cleaned, job_config=job_config, location=self.location)
        rows = query_job.result(
            max_results=self.max_result_rows,
            timeout=self.query_timeout_seconds,
        )
        bytes_processed = query_job.total_bytes_processed or dry_run.total_bytes_processed
        logger.info(
            "[REAL BigQuery] query ok job_id=%s bytes_processed=%s",
            query_job.job_id,
            bytes_processed,
        )
        return QueryResult(
            rows=[{key: _json_safe(value) for key, value in dict(row).items()} for row in rows],
            sql=cleaned,
            total_bytes_processed=bytes_processed,
        )

    def _table_ref(self, table_name: str) -> Any:
        parts = table_name.replace("`", "").split(".")
        if len(parts) == 1:
            table_id = parts[0]
        elif len(parts) == 3 and parts[:2] == [self.dataset_project_id, self.dataset_id]:
            table_id = parts[2]
        else:
            raise ValueError("Table must be in the configured BigQuery dataset.")
        if not TABLE_ID_RE.fullmatch(table_id):
            raise ValueError("Table name must be a simple table id.")
        if table_id not in self.allowed_tables:
            raise ValueError("Table is not enabled for this tutorial.")
        return self.default_dataset.table(table_id)
