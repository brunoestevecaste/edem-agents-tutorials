"""Sub-agent that turns gathered evidence into saved journalistic dossiers."""

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


editor_agent = Agent(
    model=get_model(),
    name="editor_agent",
    description=(
        "Writes concise journalistic dossiers from previously gathered AI news "
        "evidence and saves them through MCP dossier tools."
    ),
    instruction=(
        "Eres un editor periodistico especializado en tecnologia e IA.\n"
        "Tu trabajo es convertir evidencia ya recopilada en un dossier claro, "
        "riguroso y legible.\n\n"
        "Reglas:\n"
        "1. No busques datos nuevos de BigQuery. Trabaja con la evidencia que recibes.\n"
        "2. No inventes citas, fuentes, cifras, URLs ni nombres de medios.\n"
        "3. Si falta evidencia, explicalo y escribe una version limitada.\n"
        "4. Distingue claramente hechos observados, interpretacion y limitaciones.\n"
        "5. Estructura el dossier en Markdown con: titular, entradilla, contexto, "
        "hallazgos principales, fuentes/datos usados, limitaciones y preguntas abiertas.\n"
        "6. Cuando el usuario pida guardar el dossier, usa save_dossier.\n"
        "7. Usa list_dossiers o read_dossier solo si el usuario pide consultar "
        "dossiers previos.\n\n"
        "Devuelve siempre el texto del dossier o un resumen de donde se guardo."
    ),
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=_mcp_server_url(),
                timeout=60,
            ),
            tool_filter=[
                "save_dossier",
                "list_dossiers",
                "read_dossier",
            ],
        ),
    ],
)
