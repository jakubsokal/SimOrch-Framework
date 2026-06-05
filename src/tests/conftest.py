import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def sample_truths():
    return [
        {"id": "R1", "type": "FR",  "statement": "Users must be able to search for rooms by date and time."},
        {"id": "R2", "type": "FR",  "statement": "Users must be able to book, modify, and cancel reservations."},
        {"id": "R3", "type": "NFR", "statement": "The system must be accessible via web and mobile."},
    ]

@pytest.fixture
def mock_llm():
    
    llm = MagicMock()
    llm.invoke.return_value = "Mocked LLM response."
    return llm

@pytest.fixture
def re_agent_cfg():
    return {
        "name":           "Requirement Engineer",
        "role":           1,
        "provider":       "OPENAI",
        "model":          "gpt-4o-mini",
        "params":         {"temperature": 0, "max_tokens": 512},
        "context_prompt": "You are an experienced RE.",
        "api_key":        "sk-test",
        "max_words":      150,
        "persona": {
            "experience_level":     "senior",
            "questioning_strategy": "structured",
            "probing_intensity":    "medium",
            "requirement_focus":    "functional",
            "tone":                 "formal",
        },
    }

@pytest.fixture
def user_agent_cfg():
    return {
        "name":           "Jamie",
        "role":           2,
        "provider":       "OPENAI",
        "model":          "gpt-4o-mini",
        "params":         {"temperature": 0, "max_tokens": 512},
        "context_prompt": "You are Jamie, an office employee.",
        "api_key":        "sk-test",
        "persona": {
            "communication_style":    "concise",
            "domain_knowledge_level": "high",
            "clarity_level":          "clear",
            "revelation_strategy":    "proactive",
            "revelation_rate":        "medium",
        },
    }

@pytest.fixture
def helper_agent_cfg():
    return {
        "name":           "Analyst Agent",
        "role":           3,
        "provider":       "OPENAI",
        "model":          "gpt-4o-mini",
        "params":         {"temperature": 0},
        "context_prompt": "",
        "api_key":        "sk-test",
    }

@pytest.fixture
def full_scenario_config(re_agent_cfg, user_agent_cfg, helper_agent_cfg, sample_truths):
    return {
        "scenario": {
            "id":                "scenario_001",
            "seed":              42,
            "scenario_name":     "Test Scenario",
            "description":       "A test elicitation scenario.",
            "max_turns":         4,
            "conversation_type": "one_to_one",
        },
        "re_agents":      [re_agent_cfg],
        "user_agents":    [user_agent_cfg],
        "helper_agent":   helper_agent_cfg,
        "scenarioTruths": sample_truths,
    }