"""Sub-agent that gathers AI news evidence from the journalist MCP server."""

from __future__ import annotations

import os
from pathlib import Path

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    import sys

    src_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(src_dir))
    from tutorials.model_config import get_model

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MCP_SERVER_URL = "http://127.0.0.1:9002/sse"


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


def _mcp_server_url() -> str:
    _load_env_file()
    return os.getenv("MCP_SERVER_URL", DEFAULT_MCP_SERVER_URL)


news_data_agent = Agent(
    model=get_model(),
    name="news_data_agent",
    description=(
        "Searches open-data AI news signals using BigQuery-backed MCP tools. "
        "Returns structured evidence, coverage metrics, sources, and limitations."
    ),
    instruction=(
        "Eres un analista de datos abiertos especializado en noticias sobre IA.\n"
        "Tu trabajo es reunir evidencia, no redactar el articulo final.\n\n"
        "Reglas:\n"
        "1. Usa summarize_ai_news_coverage para obtener volumen, fuentes y tono medio.\n"
        "2. Usa search_ai_news para obtener ejemplos concretos de noticias o senales.\n"
        "3. No inventes datos, titulares, fuentes ni enlaces.\n"
        "4. Si las herramientas no devuelven evidencia suficiente, dilo con claridad.\n"
        "5. Devuelve una respuesta estructurada con: rango temporal, tema, metricas, "
        "hallazgos, ejemplos de fuentes/enlaces, dataset usado y limitaciones.\n"
        "6. Mantente neutral: distingue datos observados de interpretaciones.\n\n"
        "Cuando el usuario no indique fechas, pide un rango temporal concreto o usa "
        "un rango corto si el supervisor lo proporciona."
    ),
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=_mcp_server_url(),
                timeout=60,
            ),
            tool_filter=[
                "search_ai_news",
                "summarize_ai_news_coverage",
            ],
        ),
    ],
)
