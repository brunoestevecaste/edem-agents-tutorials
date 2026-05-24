"""MCP server for the AI news journalist assignment.

Run from the repository root:

    uv run python src/ai_news_journalist/mcp_server/journalist_server.py

The server exposes BigQuery-backed news search tools and dossier file tools over
SSE at http://127.0.0.1:9002/sse by default.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server import FastMCP

try:
    from ai_news_journalist.retrieval.bigquery_news import (
        search_ai_news as query_ai_news,
    )
    from ai_news_journalist.retrieval.bigquery_news import (
        summarize_ai_news_coverage as query_ai_news_summary,
    )
except ModuleNotFoundError:
    import sys

    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root / "src"))
    from ai_news_journalist.retrieval.bigquery_news import (
        search_ai_news as query_ai_news,
    )
    from ai_news_journalist.retrieval.bigquery_news import (
        summarize_ai_news_coverage as query_ai_news_summary,
    )

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "assignment_outputs" / "dossiers"

mcp = FastMCP(
    name="ai-news-journalist-mcp-server",
    host=os.getenv("AI_NEWS_MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("AI_NEWS_MCP_PORT", "9002")),
)


def _load_env_file() -> None:
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _output_dir() -> Path:
    _load_env_file()
    configured_dir = os.getenv("AI_NEWS_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))
    output_dir = Path(configured_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _safe_slug(value: str) -> str:
    slug = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "dossier"


def _safe_dossier_path(filename: str) -> Path:
    safe_name = Path(filename).name
    if not safe_name.endswith(".md"):
        safe_name = f"{safe_name}.md"
    dossier_path = (_output_dir() / safe_name).resolve()
    if _output_dir().resolve() not in dossier_path.parents:
        raise ValueError("filename must stay inside the dossier output directory.")
    return dossier_path


@mcp.tool(description="Search AI-related news signals in the public GDELT BigQuery dataset.")
def search_ai_news(
    topic: str,
    start_date: str,
    end_date: str,
    limit: int = 20,
) -> dict[str, Any]:
    """Return article-level AI news signals for a topic and date range."""
    rows = query_ai_news(
        topic=topic,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return {
        "topic": topic,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(rows),
        "rows": rows,
        "dataset": "gdelt-bq.gdeltv2.gkg_partitioned",
    }


@mcp.tool(description="Summarize AI-related news coverage volume in GDELT BigQuery.")
def summarize_ai_news_coverage(
    topic: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Return aggregate coverage metrics for an AI news topic."""
    summary = query_ai_news_summary(
        topic=topic,
        start_date=start_date,
        end_date=end_date,
    )
    summary["dataset"] = "gdelt-bq.gdeltv2.gkg_partitioned"
    return summary


@mcp.tool(description="Save a Markdown dossier with optional JSON metadata.")
def save_dossier(
    title: str,
    markdown: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Save a generated investigation dossier as a Markdown file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}-{_safe_slug(title)}.md"
    dossier_path = _output_dir() / filename

    metadata_block = {
        "title": title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **(metadata or {}),
    }
    content = (
        "<!-- metadata\n"
        f"{json.dumps(metadata_block, ensure_ascii=False, indent=2)}\n"
        "-->\n\n"
        f"# {title.strip()}\n\n"
        f"{markdown.strip()}\n"
    )
    dossier_path.write_text(content, encoding="utf-8")

    return {
        "status": "saved",
        "filename": filename,
        "path": str(dossier_path),
    }


@mcp.tool(description="List saved AI news investigation dossiers.")
def list_dossiers() -> list[dict[str, Any]]:
    """List Markdown dossiers saved by this MCP server."""
    dossiers = []
    for path in sorted(_output_dir().glob("*.md"), reverse=True):
        stat = path.stat()
        dossiers.append(
            {
                "filename": path.name,
                "path": str(path),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime,
                    tz=timezone.utc,
                ).isoformat(),
            }
        )
    return dossiers


@mcp.tool(description="Read a saved AI news investigation dossier by filename.")
def read_dossier(filename: str) -> dict[str, str]:
    """Read a previously saved Markdown dossier."""
    dossier_path = _safe_dossier_path(filename)
    if not dossier_path.exists():
        return {
            "status": "not_found",
            "filename": dossier_path.name,
            "content": "",
        }

    return {
        "status": "found",
        "filename": dossier_path.name,
        "content": dossier_path.read_text(encoding="utf-8"),
    }


if __name__ == "__main__":
    mcp.run(transport="sse")
