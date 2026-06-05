import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock
from src.orchestrator.orchestrator import Orchestrator
from src.memory.shared_memory import SharedMemory


@pytest.fixture
def re_agent():
    agent = Mock()
    agent.name = "RE"
    agent.role = 1
    agent.speak.return_value = "What features do you need?"
    return agent


@pytest.fixture
def user_agent():
    agent = Mock()
    agent.name = "User"
    agent.role = 2
    agent.speak.return_value = "I need fitness tracking features."
    return agent


@pytest.fixture
def memory():
    return SharedMemory()


@pytest.fixture
def logger():
    mock_logger = Mock()
    mock_logger.store = Mock()
    return mock_logger


@pytest.fixture
def orchestrator(re_agent, user_agent, memory, logger):
    return Orchestrator(
        max_turns=2,
        re_agents={"RE": re_agent},
        user_agents={"User": user_agent},
        helper_agent=None,
        shared_memory=memory,
        logger=logger,
    )


def test_orchestrator_init(orchestrator, re_agent, user_agent, memory, logger):
    assert isinstance(orchestrator, Orchestrator)
    assert re_agent.name in orchestrator.re_agents
    assert user_agent.name in orchestrator.user_agents
    assert orchestrator.shared_memory is memory
    assert orchestrator.logger is logger


def test_orchestrator_start_one_to_one_does_not_raise(orchestrator):
    try:
        orchestrator.start("one_to_one")
    except Exception as e:
        pytest.fail(f"start('one_to_one') raised unexpectedly: {e}")


def test_orchestrator_start_dynamic_does_not_raise(orchestrator):
    try:
        orchestrator.start("dynamic")
    except Exception as e:
        pytest.fail(f"start('dynamic') raised unexpectedly: {e}")


def test_one_to_one_writes_messages_to_memory(orchestrator, memory):
    orchestrator.start("one_to_one")
    messages = memory.get_all_messages()
    assert len(messages) > 0


def test_one_to_one_first_message_from_re(orchestrator, memory):
    orchestrator.start("one_to_one")
    messages = memory.get_all_messages()
    assert messages[0]["agent"] == "RE"


def test_one_to_one_second_message_from_user(orchestrator, memory):
    orchestrator.start("one_to_one")
    messages = memory.get_all_messages()
    assert messages[1]["agent"] == "User"


def test_max_turns_respected(orchestrator, memory):
    orchestrator.start("one_to_one")
    messages = memory.get_all_messages()
    assert len(messages) <= orchestrator.max_turns


def test_logger_store_called_after_conversation(orchestrator, logger):
    orchestrator.start("one_to_one")
    assert logger.store.called


def test_no_helper_agent_does_not_raise(re_agent, user_agent, memory, logger):
    orch = Orchestrator(
        max_turns=2,
        re_agents={"RE": re_agent},
        user_agents={"User": user_agent},
        helper_agent=None,
        shared_memory=memory,
        logger=logger,
    )
    try:
        orch.start("one_to_one")
    except Exception as e:
        pytest.fail(f"Orchestrator without helper raised unexpectedly: {e}")