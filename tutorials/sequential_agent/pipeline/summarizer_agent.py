"""Step 2: Summarizer agent — formats the researcher's findings into a report."""

from google.adk import Agent

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    from model_config import get_model


def format_report(title: str, content: str) -> str:
    """Format content into a structured report with a title and sections."""
    separator = "=" * 40
    return f"{separator}\n  {title.upper()}\n{separator}\n\n{content}\n\n{separator}"


summarizer_agent = Agent(
    model=get_model(),
    name="summarizer_agent",
    description="Reads the previous research and produces a structured report.",
    instruction=(
        "You are a report writer. Read the conversation so far — "
        "it contains raw facts from the researcher.\n"
        "Use format_report to produce a clean, structured report.\n"
        "Pass the topic as 'title' and a clear summary of the facts as 'content'.\n"
        "Do NOT invent information. Only use what the researcher provided."
    ),
    tools=[format_report],
)
