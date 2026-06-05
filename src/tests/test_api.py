import pytest
import os
from unittest.mock import MagicMock, patch

class TestProviderApiKeyEnvMapping:
    

    def _get_mapping(self):
        from llm.llm_provider_keys import PROVIDER_API_KEY_ENV
        return PROVIDER_API_KEY_ENV

    def test_openai_key_defined(self):
        mapping = self._get_mapping()
        assert "OPENAI" in mapping
        assert mapping["OPENAI"] is not None

    def test_anthropic_key_defined(self):
        mapping = self._get_mapping()
        assert "ANTHROPIC" in mapping
        assert mapping["ANTHROPIC"] is not None

    def test_groq_key_defined(self):
        mapping = self._get_mapping()
        assert "GROQ" in mapping
        assert mapping["GROQ"] is not None

    def test_gemini_key_defined(self):
        mapping = self._get_mapping()
        assert "GEMINI" in mapping
        assert mapping["GEMINI"] is not None

    def test_ollama_has_no_key(self):
        mapping = self._get_mapping()
        assert "OLLAMA" in mapping
        assert mapping["OLLAMA"] is None

    def test_no_grok_typo(self):
        
        mapping = self._get_mapping()
        assert "GROK" not in mapping

    def test_no_google_key(self):
        
        mapping = self._get_mapping()
        assert "GOOGLE" not in mapping

    def test_all_cloud_providers_have_string_env_var(self):
        mapping = self._get_mapping()
        cloud = ["OPENAI", "ANTHROPIC", "GROQ", "GEMINI"]
        for provider in cloud:
            assert isinstance(mapping[provider], str), \
                f"{provider} env var should be a non-None string"

class TestApiKeyResolution:
    

    def _resolve_key(self, provider, env_vars):
        
        PROVIDER_API_KEY_ENV = {
            "OPENAI":    "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GROQ":      "GROQ_API_KEY",
            "GEMINI":    "GEMINI_API_KEY",
            "OLLAMA":    None,
        }
        env_var = PROVIDER_API_KEY_ENV.get(provider.upper())
        if env_var is None:
            return None
        key = env_vars.get(env_var)
        if not key:
            raise ValueError(f"Set {env_var} in your .env file.")
        return key

    def test_openai_picks_up_correct_env_var(self):
        key = self._resolve_key("OPENAI", {"OPENAI_API_KEY": "sk-openai"})
        assert key == "sk-openai"

    def test_anthropic_picks_up_correct_env_var(self):
        key = self._resolve_key("ANTHROPIC", {"ANTHROPIC_API_KEY": "sk-ant-test"})
        assert key == "sk-ant-test"

    def test_groq_picks_up_correct_env_var(self):
        key = self._resolve_key("GROQ", {"GROQ_API_KEY": "gsk_test"})
        assert key == "gsk_test"

    def test_gemini_picks_up_correct_env_var(self):
        key = self._resolve_key("GEMINI", {"GEMINI_API_KEY": "gemini-key"})
        assert key == "gemini-key"

    def test_ollama_returns_none_no_key_needed(self):
        key = self._resolve_key("OLLAMA", {})
        assert key is None

    def test_missing_key_raises_value_error(self):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            self._resolve_key("OPENAI", {})

    def test_missing_groq_key_raises_value_error(self):
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            self._resolve_key("GROQ", {})

    def test_openai_key_not_used_for_groq(self):
        
        with pytest.raises(ValueError):
            self._resolve_key("GROQ", {"OPENAI_API_KEY": "sk-openai"})

    def test_case_insensitive_provider_lookup(self):
        
        key = self._resolve_key("openai", {"OPENAI_API_KEY": "sk-openai"})
        assert key == "sk-openai"

    def test_mixed_case_provider_lookup(self):
        key = self._resolve_key("Anthropic", {"ANTHROPIC_API_KEY": "sk-ant-test"})
        assert key == "sk-ant-test"

class TestAgentLoopRoleAssignment:
    

    def _run_loop(self, agent_configs):
        
        re_agents = {}
        user_agents = {}
        helper_agent = None

        for cfg in agent_configs:
            mock_agent = MagicMock()
            mock_agent.name = cfg["name"]
            mock_agent.role = cfg["role"]

            if mock_agent.role == 1:
                re_agents[mock_agent.name] = mock_agent
            elif mock_agent.role == 2:
                user_agents[mock_agent.name] = mock_agent
            elif mock_agent.role == 3:
                helper_agent = mock_agent

        return re_agents, user_agents, helper_agent

    def test_role_1_goes_to_re_agents(self):
        re, _, _ = self._run_loop([{"name": "RE", "role": 1}])
        assert "RE" in re

    def test_role_2_goes_to_user_agents(self):
        _, users, _ = self._run_loop([{"name": "Jamie", "role": 2}])
        assert "Jamie" in users

    def test_role_3_assigned_to_helper_agent(self):
        _, _, helper = self._run_loop([{"name": "Analyst", "role": 3}])
        assert helper is not None
        assert helper.name == "Analyst"

    def test_multiple_stakeholders_all_in_user_agents(self):
        cfgs = [
            {"name": "Jamie", "role": 2},
            {"name": "Sarah", "role": 2},
        ]
        _, users, _ = self._run_loop(cfgs)
        assert "Jamie" in users
        assert "Sarah" in users
        assert len(users) == 2

    def test_mixed_roles_correctly_separated(self):
        cfgs = [
            {"name": "RE",      "role": 1},
            {"name": "Jamie",   "role": 2},
            {"name": "Sarah",   "role": 2},
            {"name": "Analyst", "role": 3},
        ]
        re, users, helper = self._run_loop(cfgs)
        assert len(re) == 1
        assert len(users) == 2
        assert helper is not None

    def test_helper_agent_not_in_re_or_user_agents(self):
        cfgs = [{"name": "Analyst", "role": 3}]
        re, users, helper = self._run_loop(cfgs)
        assert len(re) == 0
        assert len(users) == 0
        assert helper is not None

    def test_no_helper_in_config_leaves_helper_none(self):
        cfgs = [
            {"name": "RE",    "role": 1},
            {"name": "Jamie", "role": 2},
        ]
        _, _, helper = self._run_loop(cfgs)
        assert helper is None