import pytest
from memory.shared_memory import SharedMemory


@pytest.fixture
def memory():
    return SharedMemory()


def test_write_and_read(memory):
    memory.write("user", "Hello, how are you?", 1, "user")
    messages = memory.get_all_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["message"] == "Hello, how are you?"


def test_multiple_writes_stored_in_order(memory):
    memory.write("RE",   "Hello! What are your requirements?", 1, "RE")
    memory.write("user", "I need the app to do XYZ.",          1, "user")
    memory.write("RE",   "So you want XYZ functionality?",     2, "RE")
    messages = memory.get_all_messages()
    assert len(messages) == 3
    assert messages[0]["role"] == "RE"
    assert messages[0]["message"] == "Hello! What are your requirements?"
    assert messages[1]["role"] == "user"
    assert messages[1]["message"] == "I need the app to do XYZ."
    assert messages[2]["role"] == "RE"
    assert messages[2]["message"] == "So you want XYZ functionality?"


def test_fresh_memory_has_no_messages(memory):
    assert memory.get_all_messages() == []


def test_write_returns_message_id(memory):
    result = memory.write("RE", "Hello", 1, 1)
    assert result is not None


def test_read_returns_last_message(memory):
    memory.write("RE",   "First",  1, 1)
    memory.write("user", "Second", 1, 2)
    last = memory.read()
    assert last["message"] == "Second"


def test_memory_is_isolated_per_instance():
    m1 = SharedMemory()
    m2 = SharedMemory()
    m1.write("RE", "Only in m1", 1, 1)
    assert len(m2.get_all_messages()) == 0