"""Safe BigQuery access helpers for AI-related open-news analysis.

The first data source for the assignment is GDELT's public GKG table in
BigQuery. This module keeps SQL generation deterministic and parameterized so
agents do not build arbitrary SQL at runtime.
"""

from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GDELT_TABLE = "gdelt-bq.gdeltv2.gkg_partitioned"
DEFAULT_MAX_BYTES_BILLED = 500_000_000
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MAX_DATE_RANGE_DAYS = 31

FORBIDDEN_SQL_KEYWORDS = (
    "ALTER",
    "CREATE",
    "DELETE",
    "DROP",
    "GRANT",
    "INSERT",
    "MERGE",
    "REPLACE",
    "REVOKE",
    "TRUNCATE",
    "UPDATE",
)

AI_SEARCH_PATTERNS = (
    "%artificial intelligence%",
    "%generative ai%",
    "%openai%",
    "%chatgpt%",
    "%anthropic%",
    "%gemini%",
    "%large language model%",
    "%llm%",
    "%machine learning%",
    "%deepfake%",
    "%nvidia%",
)

TOPIC_SYNONYMS = {
    "regulacion": ("regulation", "policy", "law", "legislation", "eu ai act"),
    "regulación": ("regulation", "policy", "law", "legislation", "eu ai act"),
    "copyright": ("copyright", "authors", "lawsuit", "licensing"),
    "chips": ("chips", "semiconductor", "nvidia", "gpu"),
    "empleo": ("jobs", "employment", "workers", "labor"),
    "educacion": ("education", "schools", "students", "teachers"),
    "educación": ("education", "schools", "students", "teachers"),
    "salud": ("healthcare", "medicine", "hospital", "patients"),
}


class BigQueryNewsError(RuntimeError):
    """Raised when the BigQuery news retrieval layer cannot run safely."""


def _load_env_file() -> None:
    """Load `.env` values if the caller has not exported them already."""
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _get_bigquery_module():
    try:
        from google.cloud import bigquery
    except ModuleNotFoundError as exc:
        raise BigQueryNewsError(
            "google-cloud-bigquery is not installed. Add it to pyproject.toml "
            "or run `uv add google-cloud-bigquery` before using BigQuery retrieval."
        ) from exc
    return bigquery


def _parse_date(value: str, field_name: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc


def _validate_date_range(start_date: str, end_date: str) -> tuple[date, date]:
    start = _parse_date(start_date, "start_date")
    end = _parse_date(end_date, "end_date")

    if start > end:
        raise ValueError("start_date cannot be later than end_date.")

    if end - start > timedelta(days=MAX_DATE_RANGE_DAYS):
        raise ValueError(
            f"Date range cannot exceed {MAX_DATE_RANGE_DAYS} days for cost control."
        )

    return start, end


def _validate_limit(limit: int) -> int:
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    return min(limit, MAX_LIMIT)


def _normalize_search_text(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _like_pattern(term: str) -> str:
    clean_term = _normalize_search_text(term)
    clean_term = clean_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{clean_term}%"


def _topic_patterns(topic: str) -> list[str]:
    normalized = _normalize_search_text(topic)
    if not normalized or normalized in {"ai", "ia", "artificial intelligence"}:
        return []

    terms = [normalized]
    for token in re.findall(r"[a-záéíóúüñ0-9]{4,}", normalized):
        terms.extend(TOPIC_SYNONYMS.get(token, ()))

    deduped_terms = list(dict.fromkeys(terms))
    return [_like_pattern(term) for term in deduped_terms]


def _max_bytes_billed() -> int:
    raw_value = os.getenv("BIGQUERY_MAX_BYTES_BILLED", str(DEFAULT_MAX_BYTES_BILLED))
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError("BIGQUERY_MAX_BYTES_BILLED must be an integer.") from exc


def _bigquery_client():
    _load_env_file()
    bigquery = _get_bigquery_module()

    project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip() or None
    return bigquery.Client(project=project)


def validate_read_only_sql(sql: str) -> None:
    """Validate that a SQL string is a single read-only SELECT query."""
    normalized = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    normalized = re.sub(r"--.*?$", " ", normalized, flags=re.MULTILINE).strip()
    upper_sql = normalized.upper()

    if not upper_sql.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    if ";" in normalized.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")

    keyword_pattern = r"\b(" + "|".join(FORBIDDEN_SQL_KEYWORDS) + r")\b"
    if re.search(keyword_pattern, upper_sql):
        raise ValueError("SQL contains a forbidden write or DDL keyword.")


def run_read_only_query(
    sql: str,
    *,
    query_parameters: list[Any] | None = None,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    """Run a validated read-only BigQuery query and return rows as dictionaries."""
    validate_read_only_sql(sql)
    safe_limit = _validate_limit(limit)
    bigquery = _get_bigquery_module()
    client = _bigquery_client()

    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=_max_bytes_billed(),
        query_parameters=query_parameters or [],
        use_query_cache=True,
    )
    rows = client.query(sql, job_config=job_config).result(max_results=safe_limit)
    return [dict(row.items()) for row in rows]


def search_ai_news(
    topic: str,
    start_date: str,
    end_date: str,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    """Search recent AI-related news signals in GDELT's public BigQuery table.

    Args:
        topic: Specific angle to search for, such as "regulation", "copyright",
            "chips", or "OpenAI". Empty or generic AI topics search broad AI news.
        start_date: Inclusive start date in YYYY-MM-DD format.
        end_date: Inclusive end date in YYYY-MM-DD format.
        limit: Maximum number of article-level rows to return.
    """
    start, end = _validate_date_range(start_date, end_date)
    safe_limit = _validate_limit(limit)
    bigquery = _get_bigquery_module()

    topic_patterns = _topic_patterns(topic)
    topic_filter_sql = ""
    if topic_patterns:
        topic_filter_sql = """
        AND EXISTS (
            SELECT 1
            FROM UNNEST(@topic_patterns) AS pattern
            WHERE searchable_text LIKE pattern
        )
        """

    sql = f"""
    SELECT
        published_date,
        source,
        url,
        avg_tone,
        themes,
        organizations,
        persons
    FROM (
        SELECT
            DATE(_PARTITIONTIME) AS published_date,
            SourceCommonName AS source,
            DocumentIdentifier AS url,
            SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) AS avg_tone,
            ARRAY_TO_STRING(
                ARRAY(
                    SELECT theme
                    FROM UNNEST(
                        SPLIT(REGEXP_REPLACE(IFNULL(V2Themes, ''), r',\\d+;', ';'), ';')
                    ) AS theme
                    WHERE theme != ''
                    LIMIT 10
                ),
                ', '
            ) AS themes,
            SUBSTR(IFNULL(V2Organizations, ''), 1, 500) AS organizations,
            SUBSTR(IFNULL(V2Persons, ''), 1, 500) AS persons,
            LOWER(
                CONCAT(
                    IFNULL(DocumentIdentifier, ''), ' ',
                    IFNULL(V2Themes, ''), ' ',
                    IFNULL(V2Organizations, ''), ' ',
                    IFNULL(V2Persons, '')
                )
            ) AS searchable_text,
            ROW_NUMBER() OVER (
                PARTITION BY DocumentIdentifier
                ORDER BY DATE DESC
            ) AS row_number
        FROM `{DEFAULT_GDELT_TABLE}`
        WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
    )
    WHERE row_number = 1
        AND EXISTS (
            SELECT 1
            FROM UNNEST(@ai_patterns) AS pattern
            WHERE searchable_text LIKE pattern
        )
        {topic_filter_sql}
    ORDER BY published_date DESC
    LIMIT @limit
    """

    query_parameters = [
        bigquery.ScalarQueryParameter("start_date", "DATE", start.isoformat()),
        bigquery.ScalarQueryParameter("end_date", "DATE", end.isoformat()),
        bigquery.ArrayQueryParameter("ai_patterns", "STRING", list(AI_SEARCH_PATTERNS)),
        bigquery.ArrayQueryParameter("topic_patterns", "STRING", topic_patterns),
        bigquery.ScalarQueryParameter("limit", "INT64", safe_limit),
    ]

    return run_read_only_query(
        sql,
        query_parameters=query_parameters,
        limit=safe_limit,
    )


def summarize_ai_news_coverage(
    topic: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Return a compact coverage summary for a topic in a date range."""
    start, end = _validate_date_range(start_date, end_date)
    bigquery = _get_bigquery_module()

    topic_patterns = _topic_patterns(topic)
    topic_filter_sql = ""
    if topic_patterns:
        topic_filter_sql = """
        AND EXISTS (
            SELECT 1
            FROM UNNEST(@topic_patterns) AS pattern
            WHERE searchable_text LIKE pattern
        )
        """

    sql = f"""
    SELECT
        COUNT(*) AS article_count,
        COUNT(DISTINCT source) AS source_count,
        ARRAY_AGG(source ORDER BY source_article_count DESC LIMIT 10) AS top_sources,
        AVG(avg_tone) AS average_tone
    FROM (
        SELECT
            source,
            avg_tone,
            COUNT(*) OVER (PARTITION BY source) AS source_article_count
        FROM (
            SELECT
                SourceCommonName AS source,
                SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) AS avg_tone,
                LOWER(
                    CONCAT(
                        IFNULL(DocumentIdentifier, ''), ' ',
                        IFNULL(V2Themes, ''), ' ',
                        IFNULL(V2Organizations, ''), ' ',
                        IFNULL(V2Persons, '')
                    )
                ) AS searchable_text
            FROM `{DEFAULT_GDELT_TABLE}`
            WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
        )
        WHERE EXISTS (
            SELECT 1
            FROM UNNEST(@ai_patterns) AS pattern
            WHERE searchable_text LIKE pattern
        )
        {topic_filter_sql}
    )
    """

    query_parameters = [
        bigquery.ScalarQueryParameter("start_date", "DATE", start.isoformat()),
        bigquery.ScalarQueryParameter("end_date", "DATE", end.isoformat()),
        bigquery.ArrayQueryParameter("ai_patterns", "STRING", list(AI_SEARCH_PATTERNS)),
        bigquery.ArrayQueryParameter("topic_patterns", "STRING", topic_patterns),
    ]

    rows = run_read_only_query(sql, query_parameters=query_parameters, limit=1)
    if not rows:
        return {
            "topic": topic,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "article_count": 0,
            "source_count": 0,
            "top_sources": [],
            "average_tone": None,
        }

    summary = rows[0]
    summary.update(
        {
            "topic": topic,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
    )
    return summary
