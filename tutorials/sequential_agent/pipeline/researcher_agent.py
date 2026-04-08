"""Step 1: Researcher agent — looks up facts from a simulated knowledge base."""

from google.adk import Agent

try:
    from tutorials.model_config import get_model
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    from model_config import get_model

KNOWLEDGE_BASE = {
    "python": (
        "Python is a high-level, interpreted programming language created by Guido van Rossum in 1991. "
        "It emphasizes readability and supports multiple paradigms including procedural, object-oriented, "
        "and functional programming. Popular libraries include NumPy, pandas, and Flask."
    ),
    "kubernetes": (
        "Kubernetes (K8s) is an open-source container orchestration platform developed by Google. "
        "It automates deployment, scaling, and management of containerized applications. "
        "Key concepts include Pods, Services, Deployments, and Namespaces."
    ),
    "mcp": (
        "The Model Context Protocol (MCP) is an open standard for connecting AI agents to external tools. "
        "An MCP server exposes tools with names, descriptions, and schemas. "
        "Clients discover tools at runtime via list_tools() and invoke them via call_tool()."
    ),
    "agents": (
        "AI agents are systems that use large language models to reason, plan, and take actions. "
        "They can call tools, access APIs, and coordinate with other agents. "
        "Common patterns include ReAct, sequential workflows, and multi-agent orchestration."
    ),
}


def search_knowledge_base(topic: str) -> str:
    """Search the knowledge base for facts about a topic."""
    key = topic.strip().lower()
    for kb_key, facts in KNOWLEDGE_BASE.items():
        if kb_key in key or key in kb_key:
            return facts
    available = ", ".join(KNOWLEDGE_BASE.keys())
    return f"No information found for '{topic}'. Available topics: {available}"


researcher_agent = Agent(
    model=get_model(),
    name="researcher_agent",
    description="Looks up facts about a topic from the knowledge base.",
    instruction=(
        "You are a researcher. When the user asks about a topic, "
        "call search_knowledge_base with that topic and return the raw facts. "
        "Do NOT summarize or reformat. Just output the facts as returned by the tool."
    ),
    tools=[search_knowledge_base],
)
