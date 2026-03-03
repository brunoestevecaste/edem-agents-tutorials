"""Remote supervisor agent exposed via A2A: orchestrates roll_die and stats agents."""

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    from model_config import get_model

roll_die_tool = AgentTool(
    agent=RemoteA2aAgent(
        name="roll_die_agent",
        description="Rolls dice and returns the results.",
        agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
    ),
)

stats_tool = AgentTool(
    agent=RemoteA2aAgent(
        name="stats_agent",
        description="Computes mean and standard deviation for a list of numbers.",
        agent_card=f"http://localhost:8002/{AGENT_CARD_WELL_KNOWN_PATH}",
    ),
)

root_agent = Agent(
    model=get_model(),
    name="supervisor_agent",
    description="Rolls dice and computes statistics by coordinating remote agents.",
    instruction=(
        "You orchestrate tasks using the available tools.\n"
        "When asked to roll dice and compute statistics:\n"
        "1. Use roll_die_agent to roll the dice.\n"
        "2. Pass the results to stats_agent.\n"
        "3. Present the rolls, mean, and standard deviation to the user."
    ),
    tools=[roll_die_tool, stats_tool],
)

supervisor_card = AgentCard(
    name="supervisor_agent",
    description=root_agent.description,
    url="http://localhost:8003",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
    skills=[
        AgentSkill(
            id="roll_and_stats",
            name="Dice Rolling & Statistics",
            description=(
                "Roll dice multiple times and compute mean and standard deviation "
                "of the results by coordinating a dice-rolling agent and a statistics agent."
            ),
            tags=["dice", "statistics", "orchestration", "multi-agent"],
            examples=[
                "Roll a 6-sided die 5 times and compute the statistics",
                "Roll a 20-sided die 10 times, then give me the mean and std",
            ],
        ),
    ],
)

a2a_app = to_a2a(root_agent, port=8003, agent_card=supervisor_card)
