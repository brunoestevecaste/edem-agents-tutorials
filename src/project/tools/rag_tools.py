"""Tool wrappers for RAG retrieval."""

from __future__ import annotations

from src.project.services.rag_service import RagService


class RagRetrievalTool:
    """Expose RAG retrieval as an agent-friendly tool call."""

    def __init__(self, rag_service: RagService) -> None:
        self.rag_service = rag_service

    def retrieve_context(self, query: str, top_k: int = 5) -> list[dict]:
        """Return retrieved documents for a user query."""
        return self.rag_service.retrieve(query=query, top_k=top_k)
