"""Supervisor agent for the AI news journalist system."""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

try:
    from ai_news_journalist.agents.editor_agent import editor_agent
    from ai_news_journalist.agents.news_data_agent import news_data_agent
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    import sys

    src_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(src_dir))
    from ai_news_journalist.agents.editor_agent import editor_agent
    from ai_news_journalist.agents.news_data_agent import news_data_agent
    from tutorials.model_config import get_model

root_agent = Agent(
    model=get_model(),
    name="ai_news_journalist_supervisor",
    description=(
        "Coordinates open-data investigations about AI news by delegating data "
        "gathering to a BigQuery-backed analyst and dossier writing to an editor."
    ),
    instruction=(
        "Eres el supervisor de un sistema multiagente de periodismo de datos "
        "sobre noticias de inteligencia artificial.\n\n"
        "Tienes dos subagentes:\n"
        "- news_data_agent: busca evidencia en datos abiertos mediante MCP y BigQuery.\n"
        "- editor_agent: redacta y guarda dossiers periodisticos a partir de evidencia.\n\n"
        "Reglas de orquestacion:\n"
        "1. Si el usuario pide investigar, tendencias, cobertura, fuentes o datos, "
        "llama a news_data_agent.\n"
        "2. Si el usuario pide redactar, resumir en formato periodistico, crear un "
        "dossier o guardar resultados, llama a editor_agent.\n"
        "3. Si el usuario pide un flujo completo, llama primero a news_data_agent "
        "y despues entrega su evidencia a editor_agent.\n"
        "4. Si faltan fechas, usa un rango corto cuando el usuario diga 'reciente' "
        "o 'esta semana'; si el encargo requiere precision, pide fechas concretas.\n"
        "5. No inventes enlaces, fuentes, cifras ni resultados de herramientas.\n"
        "6. En la respuesta final explica brevemente que datos se consultaron, "
        "que subagentes participaron y que limitaciones existen.\n\n"
        "Prioriza respuestas utiles y accionables para preparar capturas del "
        "entregable."
    ),
    tools=[
        AgentTool(agent=news_data_agent),
        AgentTool(agent=editor_agent),
    ],
)
