"""Vertex AI Search ADK agent."""

import importlib
import os
from pathlib import Path

from google.adk import Agent
from google.adk.tools import VertexAiSearchTool

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    _model_config = importlib.import_module("model_config")
    get_model = _model_config.get_model

REPO_ROOT = Path(__file__).resolve().parents[4]


def _load_env_file() -> None:
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _data_store_id() -> str:
    _load_env_file()
    data_store = os.getenv("VERTEX_SEARCH_DATA_STORE_ID", "").strip()
    if not data_store:
        raise RuntimeError(
            "VERTEX_SEARCH_DATA_STORE_ID is not configured. "
            "Run notebooks/vertex_search_indexing.ipynb first, then copy the value to .env."
        )
    return data_store


vertex_search_tool = VertexAiSearchTool(
    data_store_id=_data_store_id(),
)

root_agent = Agent(
    model=get_model(),
    name="vertex_search_agent",
    description="Answers questions about documents indexed in a Vertex AI Search data store.",
    instruction=(
        "You answer questions about documents stored in a Vertex AI Search data store.\n"
        "Use the grounded search results to answer questions about the indexed documents.\n"
        "Keep your answers concise and based on the retrieved context.\n"
        "If the data store does not contain enough information, say so."
    ),
    tools=[vertex_search_tool],
)
