"""Smoke tests for ADK agent declarations."""

import pytest

pytest.importorskip("google.adk")

from orchestrator.agent import root_agent
from orchestrator.rag_agent import rag_agent
from orchestrator.talk_with_data_agent import talk_with_data_agent


def test_agents_are_named() -> None:
    assert root_agent.name == "orchestrator_agent"
    assert rag_agent.name == "rag_agent"
    assert talk_with_data_agent.name == "talk_with_data_agent"
