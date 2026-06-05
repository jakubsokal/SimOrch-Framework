import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, MagicMock
from src.agents.user_agent import UserAgent
from src.agents.base_agent import BaseAgent


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke.return_value = MagicMock(content="Mocked user response.")
    return llm


@pytest.fixture
def user_agent(mock_llm):
    return UserAgent("TestUser", llm=mock_llm, role=2, persona={
        "communication_style": "concise",
        "domain_knowledge_level": "high",
        "clarity_level": "clear",
        "revelation_strategy": "proactive",
        "revelation_rate": "medium",
        }, context_prompt="You are Jamie, an office employee.")


def test_init_sets_name(user_agent):
    assert user_agent.name == "TestUser"


def test_inherits_from_base_agent(user_agent):
    assert isinstance(user_agent, BaseAgent)


def test_speak_returns_a_string(user_agent):
    result = user_agent.speak("What do you need?", role=1)
    assert isinstance(result, str)


def test_speak_invokes_llm(mock_llm, user_agent):
    user_agent.speak("Hello", role=1)
    assert mock_llm.invoke.called


def test_speak_with_empty_message_does_not_raise(user_agent):
    try:
        user_agent.speak("", role=1)
    except Exception as e:
        pytest.fail(f"speak('', role=1) raised unexpectedly: {e}")


def test_multiple_agents_are_independent(mock_llm):
    mock_llm2 = Mock()
    mock_llm2.invoke.return_value = MagicMock(content="Second response.")
    agent1 = UserAgent("Agent1", llm=mock_llm)
    agent2 = UserAgent("Agent2", llm=mock_llm2)
    assert agent1.name == "Agent1"
    assert agent2.name == "Agent2"
    assert agent1.name != agent2.name


def test_persona_stored_on_agent(mock_llm):
    persona = {"communication_style": "concise", "tone": "formal"}
    agent = UserAgent("Jamie", llm=mock_llm, persona=persona)
    assert agent.persona == persona


def test_scenario_truths_stored_on_agent(mock_llm):
    truths = [{"id": "R1", "type": "FR", "statement": "Users must log in."}]
    agent = UserAgent("Jamie", llm=mock_llm, scenario_truths=truths)
    assert agent.scenario_truths == truths