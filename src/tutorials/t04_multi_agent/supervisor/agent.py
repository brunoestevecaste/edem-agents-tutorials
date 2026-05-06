"""Supervisor agent: orchestrates roll_die and stats agents locally using AgentTool."""

from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

from tutorials.model_config import get_model
from .roll_die_agent import roll_die_agent
from .stats_agent import stats_agent

root_agent = Agent(
    model=get_model(),
    name="supervisor_agent",
    description="Rolls dice and computes statistics by coordinating local sub-agents.",
    instruction=(
        "You orchestrate tasks using the available tools.\n"
        "When asked to roll dice and compute statistics:\n"
        "1. Use roll_die_agent to roll the dice.\n"
        "2. Pass the results to stats_agent.\n"
        "3. Present the rolls, mean, and standard deviation to the user."
    ),
    tools=[
        AgentTool(agent=roll_die_agent),
        AgentTool(agent=stats_agent),
    ],
)
