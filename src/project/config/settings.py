"""Configuration loader for the educational multi-agent project."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    google_cloud_project: str
    google_cloud_location: str
    bigquery_dataset_project: str
    bigquery_dataset: str
    bigquery_allowed_tables: list[str]
    bigquery_location: str
    bigquery_max_bytes_billed: int
    bigquery_query_timeout_seconds: int
    bigquery_max_result_rows: int
    rag_corpus_id: str
    model_name: str
    use_mock_services: bool


def get_settings() -> Settings:
    """Return application settings."""
    return Settings(
        google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        google_cloud_location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        bigquery_dataset_project=os.getenv("BIGQUERY_DATASET_PROJECT", "bigquery-public-data"),
        bigquery_dataset=os.getenv("BIGQUERY_DATASET", "thelook_ecommerce"),
        bigquery_allowed_tables=[
            table.strip()
            for table in os.getenv(
                "BIGQUERY_ALLOWED_TABLES",
                "users,orders,order_items,products,inventory_items",
            ).split(",")
            if table.strip()
        ],
        bigquery_location=os.getenv("BIGQUERY_LOCATION", "US"),
        bigquery_max_bytes_billed=int(os.getenv("BIGQUERY_MAX_BYTES_BILLED", "1000000000")),
        bigquery_query_timeout_seconds=int(os.getenv("BIGQUERY_QUERY_TIMEOUT_SECONDS", "30")),
        bigquery_max_result_rows=int(os.getenv("BIGQUERY_MAX_RESULT_ROWS", "100")),
        rag_corpus_id=os.getenv("RAG_CORPUS_ID", "demo_corpus"),
        model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
        use_mock_services=os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    )
