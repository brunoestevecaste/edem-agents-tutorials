"""Root agent: routes questions to RAG and data agents."""

from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

from tutorials.model_config import get_model

from .rag_agent import rag_agent
from .talk_with_data_agent import talk_with_data_agent

root_agent = Agent(
    model=get_model(),
    name="orchestrator_agent",
    description="Routes user questions to RAG, Talk with Data, or both.",
    instruction=(
        "You are an orchestrator. Use ReAct: choose the needed agent tool, call it, observe, then answer.\n"
        "Use rag_agent for policy, documentation, and conceptual questions.\n"
        "Use talk_with_data_agent for metrics, KPIs, counts, aggregations, trends, and SQL questions.\n"
        "Use both when the user asks to interpret data against policy or documentation.\n"
        "Keep the final answer concise and include sources or SQL when available."
    ),
    tools=[
        AgentTool(agent=rag_agent),
        AgentTool(agent=talk_with_data_agent),
    ],
)
