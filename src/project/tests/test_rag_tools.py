"""Tests for RAG retrieval tools."""

from services.rag_service import MockRagService


def test_rag_service_retrieves_matching_context() -> None:
    docs = MockRagService().retrieve("return rates product categories")
    assert docs
    assert docs[0]["source"] == "refund_policy.md"


def test_rag_service_returns_empty_when_context_is_missing() -> None:
    docs = MockRagService().retrieve("quantum foam tax rules")
    assert docs == []
