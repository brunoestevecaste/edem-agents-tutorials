"""RAG agent: answers from retrieved context."""

from google.adk import Agent

from tutorials.model_config import get_model

from src.project.services.rag_service import MockRagService

rag = MockRagService()


def retrieve_context(query: str, top_k: int = 3) -> list[dict]:
    """Retrieve context documents for a user query."""
    return rag.retrieve(query=query, top_k=top_k)


rag_agent = Agent(
    model=get_model(),
    name="rag_agent",
    description="Answers questions using retrieved documents.",
    instruction=(
        "You are a RAG agent. Use ReAct: retrieve context, observe it, then answer.\n"
        "Always call retrieve_context before answering.\n"
        "Answer only from retrieved context.\n"
        "Cite sources when available.\n"
        "If there is not enough context, say so."
    ),
    tools=[retrieve_context],
)
