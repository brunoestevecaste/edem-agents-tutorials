"""RAG service abstractions for local mocks and future Vertex AI integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class RetrievedDocument:
    """A retrieved chunk from a RAG store."""

    id: str
    source: str
    content: str


class RagService(Protocol):
    """Interface for retrieving documents from a RAG backend."""

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Return ranked context documents for a query."""


class MockRagService:
    """Deterministic in-memory RAG retriever for local learning and tests."""

    def __init__(self) -> None:
        self._docs: list[RetrievedDocument] = [
            RetrievedDocument(
                id="policy-1",
                source="revenue_recognition_policy.md",
                content="Revenue is recognized when an order is shipped and payment is captured.",
            ),
            RetrievedDocument(
                id="policy-2",
                source="refund_policy.md",
                content="Product categories with return rates above 12 percent require weekly review.",
            ),
            RetrievedDocument(
                id="policy-3",
                source="inventory_risk_policy.md",
                content="Products with high sales and low remaining inventory should be restocking priorities.",
            ),
            RetrievedDocument(
                id="policy-4",
                source="regional_sales_targets.md",
                content="Regions below monthly sales targets require an action plan from the retail operations team.",
            ),
            RetrievedDocument(
                id="policy-5",
                source="marketing_kpi_definitions.md",
                content="Conversion trends should be interpreted by traffic source, order count, and revenue.",
            ),
        ]

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Return documents using simple keyword-overlap scoring."""
        terms = {token.strip("?,.!").lower() for token in query.split() if token.strip()}
        scored: list[tuple[int, RetrievedDocument]] = []
        for doc in self._docs:
            doc_terms = set(doc.content.lower().split())
            score = len(terms & doc_terms)
            if score:
                scored.append((score, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {"id": d.id, "source": d.source, "content": d.content}
            for _, d in scored[:top_k]
        ]


class VertexRagService:
    """Placeholder for future Vertex AI / Agent Platform RAG Engine integration."""

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve from Vertex AI RAG Engine.

        TODO: Replace this stub with real Vertex AI SDK calls:
        1. Use corpus from RAG_CORPUS_ID.
        2. Submit query embeddings/search against the corpus.
        3. Return normalized list[{id, source, content}].
        """
        raise NotImplementedError("VertexRagService integration is not implemented yet.")
