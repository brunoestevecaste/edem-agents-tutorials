"""Local agent: computes distribution statistics (mean and standard deviation)."""

import math

from google.adk import Agent

from tutorials.model_config import get_model


def compute_mean(numbers: list[float]) -> float:
    """Compute the arithmetic mean of a list of numbers."""
    return sum(numbers) / len(numbers)


def compute_std(numbers: list[float]) -> float:
    """Compute the standard deviation of a list of numbers."""
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return math.sqrt(variance)


stats_agent = Agent(
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
    tools=[compute_mean, compute_std],
)
