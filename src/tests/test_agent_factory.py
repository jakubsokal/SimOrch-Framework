import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def base_cfg():
    
    return {
        "name":           "RE Agent",
        "role":           1,
        "provider":       "OPENAI",
        "model":          "gpt-4o-mini",
        "params":         {"temperature": 0, "max_tokens": 512},
        "context_prompt": "You are an RE agent.",
        "api_key":        "sk-test-key",
        "max_words":      150,
        "persona":        {"tone": "formal"},
    }

@pytest.fixture
def user_cfg():
    return {
        "name":           "Jamie",
        "role":           2,
        "provider":       "OPENAI",
        "model":          "gpt-4o-mini",
        "params":         {"temperature": 0, "max_tokens": 512},
        "context_prompt": "You are Jamie.",
        "api_key":        "sk-test-key",
        "persona":        {"communication_style": "concise"},
    }

@pytest.fixture
def helper_cfg():
    return {
        "name":           "Analyst Agent",
        "role":           3,
        "provider":       "OPENAI",
        "model":          "gpt-4o-mini",
        "params":         {"temperature": 0},
        "context_prompt": "",
        "api_key":        "sk-test-key",
    }

def make_agent(cfg, description="Test scenario", seed=42, truths=None):
    
    from src.agents.agent_factory import AgentFactory
    with patch("src.agents.agent_factory.LLMFactory.create_llm", return_value=MagicMock()):
        return AgentFactory.create_agent(cfg, description, seed=seed, scenarioTruths=truths)

class TestAgentFactoryRoleMapping:
    def test_role_1_creates_re_agent(self, base_cfg):
        from src.agents.re_agent import REAgent
        agent = make_agent(base_cfg)
        assert isinstance(agent, REAgent)

    def test_role_2_creates_user_agent(self, user_cfg):
        from src.agents.user_agent import UserAgent
        agent = make_agent(user_cfg)
        assert isinstance(agent, UserAgent)

    def test_role_3_creates_helper_agent(self, helper_cfg):
        from src.agents.helper_agent import HelperAgent
        agent = make_agent(helper_cfg)
        assert isinstance(agent, HelperAgent)

    def test_unknown_role_raises_value_error(self, base_cfg):
        from src.agents.agent_factory import AgentFactory
        bad_cfg = {**base_cfg, "role": 99}
        with patch("src.agents.agent_factory.LLMFactory.create_llm", return_value=MagicMock()):
            with pytest.raises((ValueError, KeyError)):
                AgentFactory.create_agent(bad_cfg, "desc", seed=42)

class TestAgentFactoryAttributes:
    def test_name_assigned(self, base_cfg):
        agent = make_agent(base_cfg)
        assert agent.name == "RE Agent"

    def test_role_assigned(self, base_cfg):
        agent = make_agent(base_cfg)
        assert agent.role == 1

    def test_description_assigned(self, base_cfg):
        agent = make_agent(base_cfg, description="Meeting room scenario")
        assert agent.description == "Meeting room scenario"

    def test_max_words_assigned(self, base_cfg):
        agent = make_agent(base_cfg)
        assert agent.max_words == 150

    def test_max_words_defaults_to_500_when_absent(self, base_cfg):
        cfg = {k: v for k, v in base_cfg.items() if k != "max_words"}
        agent = make_agent(cfg)
        assert agent.max_words == 500

    def test_persona_assigned(self, base_cfg):
        agent = make_agent(base_cfg)
        assert agent.persona == {"tone": "formal"}

    def test_context_prompt_assigned(self, base_cfg):
        agent = make_agent(base_cfg)
        assert agent.context_prompt == "You are an RE agent."

class TestScenarioTruthsAssignment:
    TRUTHS = [{"id": "R1", "type": "FR", "statement": "Users must log in."}]

    def test_user_agent_receives_scenario_truths(self, user_cfg):
        agent = make_agent(user_cfg, truths=self.TRUTHS)
        assert agent.scenario_truths == self.TRUTHS

    def test_re_agent_does_not_receive_scenario_truths(self, base_cfg):
        agent = make_agent(base_cfg, truths=self.TRUTHS)
        assert agent.scenario_truths is None

    def test_helper_agent_does_not_receive_scenario_truths(self, helper_cfg):
        agent = make_agent(helper_cfg, truths=self.TRUTHS)
        assert agent.scenario_truths is None

    def test_user_agent_truths_none_when_not_provided(self, user_cfg):
        agent = make_agent(user_cfg, truths=None)
        assert agent.scenario_truths is None

class TestAgentFactoryLLMCall:
    def test_llm_factory_called_once(self, base_cfg):
        from src.agents.agent_factory import AgentFactory
        with patch("src.agents.agent_factory.LLMFactory.create_llm", return_value=MagicMock()) as mock_llm:
            AgentFactory.create_agent(base_cfg, "desc", seed=42)
            mock_llm.assert_called_once()

    def test_llm_factory_receives_seed(self, base_cfg):
        from src.agents.agent_factory import AgentFactory
        with patch("src.agents.agent_factory.LLMFactory.create_llm", return_value=MagicMock()) as mock_llm:
            AgentFactory.create_agent(base_cfg, "desc", seed=99)
            _, kwargs = mock_llm.call_args
            assert kwargs.get("seed") == 99 or mock_llm.call_args[0][1] == 99

    def test_llm_factory_receives_cfg_with_api_key(self, base_cfg):
        from src.agents.agent_factory import AgentFactory
        with patch("src.agents.agent_factory.LLMFactory.create_llm", return_value=MagicMock()) as mock_llm:
            AgentFactory.create_agent(base_cfg, "desc", seed=42)
            passed_cfg = mock_llm.call_args[0][0]
            assert passed_cfg.get("api_key") == "sk-test-key"