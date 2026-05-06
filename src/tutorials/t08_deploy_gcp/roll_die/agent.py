"""Deployable ADK agent: rolls dice using a Python function tool."""

import os
import random

from google.adk import Agent


def get_model() -> str:
    """Return a Vertex AI Gemini model name for Cloud Run or Agent Engine."""
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    return os.getenv("VERTEX_MODEL", "gemini-2.5-flash-lite")


def roll_die(sides: int) -> int:
    """Roll a die with the given number of sides. Returns the result (1 to sides)."""
    return random.randint(1, sides)


root_agent = Agent(
    model=get_model(),
    name="roll_die_agent",
    description="Rolls dice with a configurable number of sides.",
    instruction=(
        "You are a dice-rolling assistant. You can ONLY roll dice using the roll_die tool.\n"
        "When asked to roll a die N times, call roll_die once for EACH roll requested.\n"
        "Always reply with the results as a comma-separated list, e.g.: 'Results: 3, 5, 1, 6, 2'.\n"
        "If the user does not specify the number of sides, assume 6.\n"
        "Do NOT make up results. Always call the roll_die tool."
    ),
    tools=[roll_die],
)
