"""Root agent: routes questions to RAG and data agents."""

from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

from config.model import get_model

from .rag_agent import rag_agent
from .talk_with_data_agent import talk_with_data_agent

root_agent = Agent(
    model=get_model(),
    name="orchestrator_agent",
    description="Routes TheLook retail analytics questions to RAG, Talk with Data, or both.",
    instruction=(
        "You are the orchestrator for TheLook Retail Intelligence Assistant.\n"
        "Use ReAct: choose the needed agent tool, call it, observe, then answer.\n"
        "Use rag_agent for refund, revenue, inventory, regional target, segmentation, and marketing policies.\n"
        "Use talk_with_data_agent for TheLook ecommerce metrics, orders, returns, products, customers, and inventory.\n"
        "Use both when the user asks to interpret BigQuery data against company policy or targets.\n"
        "Keep the final answer concise and include sources or SQL when available."
    ),
    tools=[
        AgentTool(agent=rag_agent),
        AgentTool(agent=talk_with_data_agent),
    ],
)
