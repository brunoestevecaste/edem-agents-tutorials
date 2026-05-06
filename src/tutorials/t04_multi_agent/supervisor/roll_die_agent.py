"""Local agent: rolls dice."""

import random

from google.adk import Agent

from tutorials.model_config import get_model


def roll_die(sides: int) -> int:
    """Roll a die with the given number of sides. Returns the result (1 to sides)."""
    return random.randint(1, sides)


roll_die_agent = Agent(
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
