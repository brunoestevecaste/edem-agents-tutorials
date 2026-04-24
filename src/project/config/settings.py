"""Configuration loader for the educational multi-agent project."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "demo_sales")
    bigquery_location: str = os.getenv("BIGQUERY_LOCATION", "US")
    rag_corpus_id: str = os.getenv("RAG_CORPUS_ID", "demo_corpus")
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    use_mock_services: bool = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()
