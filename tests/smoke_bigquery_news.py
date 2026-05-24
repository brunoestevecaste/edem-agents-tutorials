"""Smoke test script for the AI news BigQuery retrieval layer.

Run manually from the repository root:

    uv run python tests/smoke_bigquery_news.py

This script calls the public GDELT BigQuery dataset using Application Default
Credentials. It is intentionally not named `test_*.py` because it requires GCP
credentials and may incur BigQuery usage.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


def main() -> None:
    from ai_news_journalist.retrieval.bigquery_news import (
        search_ai_news,
        summarize_ai_news_coverage,
    )

    end_date = date.today() - timedelta(days=2)
    start_date = end_date

    start = start_date.isoformat()
    end = end_date.isoformat()
    topic = "regulation"

    print(f"Querying AI news for topic={topic!r}, start={start}, end={end}")

    summary = summarize_ai_news_coverage(
        topic=topic,
        start_date=start,
        end_date=end,
    )
    print("\nCoverage summary:")
    print(summary)

    rows = search_ai_news(
        topic=topic,
        start_date=start,
        end_date=end,
        limit=5,
    )
    print(f"\nTop {len(rows)} rows:")
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}. {row.get('published_date')} | "
            f"{row.get('source')} | {row.get('url')}"
        )


if __name__ == "__main__":
    main()
