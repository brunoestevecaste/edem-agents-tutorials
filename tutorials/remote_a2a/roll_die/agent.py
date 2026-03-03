"""Remote agent exposed via A2A: rolls a die."""

import random

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.examples.example import Example
from google.adk.tools.example_tool import ExampleTool
from google.genai import types

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    from model_config import get_model


def roll_die(sides: int) -> int:
    """Roll a die with the given number of sides. Returns the result (1 to sides)."""
    return random.randint(1, sides)

root_agent = Agent(
    model=get_model(),
    name="roll_die_agent",
    description=(
        "Rolls dice. Input: how many rolls and how many sides (default 6). "
        "Output: comma-separated results, e.g. 'Results: 3, 5, 1, 6, 2'."
    ),
    instruction=(
        "You are a dice-rolling assistant. You can ONLY roll dice using the roll_die tool.\n"
        "When asked to roll a die N times, call roll_die once for EACH roll requested.\n"
        "Always reply with the results as a comma-separated list, e.g.: 'Results: 3, 5, 1, 6, 2'.\n"
        "If the user does not specify the number of sides, assume 6.\n"
        "Do NOT make up results. Always call the roll_die tool."
    ),
    tools=[roll_die],
)

roll_die_card = AgentCard(
    name="roll_die_agent",
    description=root_agent.description,
    url="http://localhost:8001",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
    skills=[
        AgentSkill(
            id="roll_die",
            name="Dice Rolling",
            description="Roll one or more dice with a configurable number of sides.",
            tags=["dice", "random", "simulation"],
            examples=[
                "Roll a 6-sided die 3 times",
                "Roll a 20-sided die",
                "Roll a die 10 times",
            ],
        ),
    ],
)

a2a_app = to_a2a(root_agent, port=8001, agent_card=roll_die_card)
