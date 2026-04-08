"""Sequential workflow: researcher runs first, then summarizer. Order is fixed in code."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from google.adk.agents import SequentialAgent

from researcher_agent import researcher_agent
from summarizer_agent import summarizer_agent

root_agent = SequentialAgent(
    name="pipeline_agent",
    sub_agents=[researcher_agent, summarizer_agent],
)
