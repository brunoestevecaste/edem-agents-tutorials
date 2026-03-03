"""Remote agent exposed via A2A: computes distribution statistics."""

import math

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


def compute_mean(numbers: list[float]) -> float:
    """Compute the arithmetic mean of a list of numbers."""
    return sum(numbers) / len(numbers)


def compute_std(numbers: list[float]) -> float:
    """Compute the standard deviation of a list of numbers."""
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return math.sqrt(variance)


stats_examples = ExampleTool(
    examples=[
        Example(
            input=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Compute stats for: 3, 5, 1, 6, 2")],
            ),
            output=[
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="Mean: 3.4, Std: 1.74")],
                )
            ],
        ),
    ]
)

root_agent = Agent(
    model=get_model(),
    name="stats_agent",
    description=(
        "Computes statistics. Input: a list of numbers. "
        "Output: mean and standard deviation, e.g. 'Mean: 3.5, Std: 1.71'."
    ),
    instruction=(
        "You are a statistics assistant. You can ONLY compute mean and standard deviation.\n"
        "When you receive a list of numbers, you MUST:\n"
        "1. Call compute_mean with the list of numbers.\n"
        "2. Call compute_std with the same list of numbers.\n"
        "3. Reply with both results clearly, e.g.: 'Mean: 3.5, Std: 1.71'.\n"
        "Do NOT compute anything yourself. Always call both tools.\n"
        "Extract numbers from the message even if they are embedded in text."
    ),
    tools=[compute_mean, compute_std, stats_examples],
)

stats_card = AgentCard(
    name="stats_agent",
    description=root_agent.description,
    url="http://localhost:8002",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
    skills=[
        AgentSkill(
            id="compute_mean",
            name="Mean Calculation",
            description="Compute the arithmetic mean of a list of numbers.",
            tags=["statistics", "math", "mean", "average"],
            examples=["Compute the mean of: 3, 5, 1, 6, 2"],
        ),
        AgentSkill(
            id="compute_std",
            name="Standard Deviation",
            description="Compute the population standard deviation of a list of numbers.",
            tags=["statistics", "math", "std", "deviation"],
            examples=["What is the standard deviation of 10, 20, 30?"],
        ),
    ],
)

a2a_app = to_a2a(root_agent, port=8002, agent_card=stats_card)
