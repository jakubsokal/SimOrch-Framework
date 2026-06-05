import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, MagicMock
from src.agents.re_agent import REAgent
from src.agents.base_agent import BaseAgent


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke.return_value = MagicMock(content="Mocked RE response.")
    return llm


@pytest.fixture
def re_agent(mock_llm):
    return REAgent("TestRE", llm=mock_llm, role=1, persona={
        "experience_level": "senior",
        "questioning_strategy": "structured",
        "probing_intensity": "medium",
        "requirement_focus": "functional",
        "tone": "formal",
    }, context_prompt="You are an experienced RE.")


def test_init_sets_name(re_agent):
    assert re_agent.name == "TestRE"


def test_inherits_from_base_agent(re_agent):
    assert isinstance(re_agent, BaseAgent)


def test_speak_returns_a_string(re_agent):
    result = re_agent.speak(None, None)
    assert isinstance(result, str)


def test_speak_with_user_message_returns_string(re_agent):
    result = re_agent.speak("I need a booking system.", role=2)
    assert isinstance(result, str)


def test_speak_with_re_message_returns_string(re_agent):
    result = re_agent.speak("What features do you need?", role=1)
    assert isinstance(result, str)


def test_speak_invokes_llm(mock_llm, re_agent):
    re_agent.speak(None, None)
    assert mock_llm.invoke.called


def test_multiple_agents_are_independent(mock_llm):
    mock_llm2 = Mock()
    mock_llm2.invoke.return_value = MagicMock(content="Second response.")
    agent1 = REAgent("Agent1", llm=mock_llm)
    agent2 = REAgent("Agent2", llm=mock_llm2)
    assert agent1.name == "Agent1"
    assert agent2.name == "Agent2"
    assert agent1.name != agent2.name


def test_speak_none_message_does_not_raise(re_agent):
    try:
        re_agent.speak(None, None)
    except Exception as e:
        pytest.fail(f"speak(None, None) raised unexpectedly: {e}")