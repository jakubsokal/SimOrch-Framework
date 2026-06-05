import pytest
from unittest.mock import MagicMock

def make_agent(**kwargs):
    from src.agents.base_agent import BaseAgent

    class ConcreteAgent(BaseAgent):
        def speak(self, message, role):
            return "hello"

    defaults = dict(
        name="Test Agent",
        llm=MagicMock(),
        role=1,
        context_prompt="",
        description="test",
        max_words=512,
        persona=None,
        scenario_truths=None,
    )
    defaults.update(kwargs)
    return ConcreteAgent(**defaults)

class TestBaseAgentInit:
    def test_name_stored(self):
        agent = make_agent(name="Alice")
        assert agent.name == "Alice"

    def test_role_stored(self):
        agent = make_agent(role=2)
        assert agent.role == 2

    def test_max_words_default(self):
        agent = make_agent()
        assert agent.max_words == 512

    def test_max_words_custom(self):
        agent = make_agent(max_words=200)
        assert agent.max_words == 200

    def test_persona_none_by_default(self):
        agent = make_agent()
        assert agent.persona is None

    def test_scenario_truths_none_by_default(self):
        agent = make_agent()
        assert agent.scenario_truths is None

    def test_llm_stored_as_agent(self):
        mock_llm = MagicMock()
        agent = make_agent(llm=mock_llm)
        assert agent.agent is mock_llm

class TestGetResponse:
    def _call(self, value):
        from src.agents.base_agent import BaseAgent
        return BaseAgent.get_response(value)

    def test_none_returns_none(self):
        assert self._call(None) is None

    def test_string_returned_as_is(self):
        assert self._call("hello world") == "hello world"

    def test_empty_string_returned(self):
        assert self._call("") == ""

    def test_object_with_content_attribute(self):
        mock_response = MagicMock()
        mock_response.content = "extracted content"
        assert self._call(mock_response) == "extracted content"

    def test_object_without_content_falls_back_to_str(self):
        class NoContent:
            def __str__(self):
                return "stringified"
        assert self._call(NoContent()) == "stringified"

    def test_content_none_falls_back_to_str(self):
        mock_response = MagicMock()
        mock_response.content = None
        result = self._call(mock_response)
        assert isinstance(result, str)

class TestGetScenarioTruthsFormatted:
    def test_none_truths_returns_empty_string(self):
        agent = make_agent(scenario_truths=None)
        assert agent.get_scenario_truths_formatted() == ""

    def test_empty_list_returns_empty_string(self):
        agent = make_agent(scenario_truths=[])
        assert agent.get_scenario_truths_formatted() == ""

    def test_string_truths_returned_as_is(self):
        agent = make_agent(scenario_truths="raw string truths")
        assert agent.get_scenario_truths_formatted() == "raw string truths"

    def test_non_list_non_string_falls_back_to_str(self):
        agent = make_agent(scenario_truths=42)
        result = agent.get_scenario_truths_formatted()
        assert result == "42"

    def test_single_truth_formatted_correctly(self):
        truths = [{"id": "R1", "type": "FR", "statement": "Users must log in."}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted()
        assert "R1" in result
        assert "FR" in result
        assert "Users must log in." in result

    def test_multiple_truths_each_on_own_line(self):
        truths = [
            {"id": "R1", "type": "FR",  "statement": "Users must log in."},
            {"id": "R2", "type": "NFR", "statement": "System must be fast."},
        ]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted()
        lines = result.strip().split("\n")
        assert len(lines) == 2

    def test_truth_without_type_still_formats(self):
        truths = [{"id": "R1", "statement": "Some requirement."}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted()
        assert "R1" in result
        assert "Some requirement." in result

    def test_truth_without_id_uses_question_mark(self):
        truths = [{"type": "FR", "statement": "No id here."}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted()
        assert "?" in result

    def test_long_statement_truncated(self):
        long_stmt = "A" * 300
        truths = [{"id": "R1", "type": "FR", "statement": long_stmt}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted(max_chars_per_statement=100)
        assert result.endswith("…")
        assert len(result) < 300

    def test_statement_within_limit_not_truncated(self):
        stmt = "Short statement."
        truths = [{"id": "R1", "type": "FR", "statement": stmt}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted(max_chars_per_statement=240)
        assert "…" not in result
        assert "Short statement." in result

    def test_non_dict_truth_handled_gracefully(self):
        truths = ["plain string truth", {"id": "R1", "statement": "dict truth"}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted()
        assert "plain string truth" in result
        assert "R1" in result

    def test_whitespace_normalised_in_statement(self):
        truths = [{"id": "R1", "type": "FR", "statement": "Users   must   log   in."}]
        agent = make_agent(scenario_truths=truths)
        result = agent.get_scenario_truths_formatted()
        assert "Users must log in." in result

    def test_speak_raises_not_implemented_on_base(self):
        from src.agents.base_agent import BaseAgent
        agent = BaseAgent.__new__(BaseAgent)
        with pytest.raises(NotImplementedError):
            agent.speak("msg", 1)