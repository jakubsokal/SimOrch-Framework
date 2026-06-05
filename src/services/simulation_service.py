import copy
import random
import datetime
import time
from ..orchestrator import Orchestrator
from ..agents import AgentFactory
from ..memory import SharedMemory
from ..logs import Logger
from ..llm.llm_provider_keys import PROVIDER_API_KEY_ENV
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def _sanitise_config(config: dict) -> dict:
    safe = copy.deepcopy(config)
    for agent in (
        safe.get("re_agents", []) +
        safe.get("user_agents", []) +
        ([safe.get("helper_agent")] if safe.get("helper_agent") else [])
    ):
        if isinstance(agent, dict):
            agent.pop("api_key", None)
    return safe


def run_simulation(config: dict):
    timestamp = datetime.datetime.now().isoformat()
    start_time = time.time()
    logger = Logger(scenario_id=config.get("scenario", {}).get("id", None))
    status = "completed"
    error = None
    seed = None
    turn_counter = 1

    print(f"[Simulation] Starting at {timestamp} with config: {config.get('scenario', {}).get('scenario_name', '')}")

    seed = config.get("scenario", {}).get("seed")
    random.seed(seed)
    description = config.get("scenario", {}).get("description", "")
    max_turns = config.get("scenario", {}).get("max_turns", 10)
    scenarioTruths = config.get("scenarioTruths", None)

    agent_configs = (
        config.get("re_agents", []) +
        config.get("user_agents", []) +
        ([config.get("helper_agent")] if config.get("helper_agent") else [])
    )

    try:
        re_agents = {}
        user_agents = {}
        helper_agent = None

        for agent_config in agent_configs:
            provider = agent_config.get("provider", "").upper()
            env_var = PROVIDER_API_KEY_ENV.get(provider)
            env_key = os.getenv(env_var) if env_var else None
            ui_key = agent_config.get("api_key", "").strip() if isinstance(agent_config.get("api_key"), str) else ""
            effective_api_key = env_key or ui_key or None

            if env_var and not effective_api_key:
                raise ValueError(
                    f"Provider '{provider}' requires an API key. "
                    f"Set {env_var} in your .env file or supply it in the request."
                )

            agent_cfg = {**agent_config, 'api_key': effective_api_key}
            agent = AgentFactory.create_agent(
                agent_cfg, description, seed=seed, scenarioTruths=scenarioTruths
            )

            if agent.role == 1:
                re_agents[agent.name] = agent
            elif agent.role == 2:
                user_agents[agent.name] = agent
            elif agent.role == 3:
                helper_agent = agent

            print(f"[LLM Factory] Created agent: {agent.name} Role: ({agent.role})")

        orchestrator = Orchestrator(
            re_agents=re_agents,
            user_agents=user_agents,
            helper_agent=helper_agent,
            max_turns=max_turns,
            shared_memory=SharedMemory(),
            logger=logger,
        )

        conversation_type = config.get("scenario", {}).get("conversation_type", "dynamic")
        orchestrator.start(conversation_type)
        turn_counter = orchestrator.turn_counter
        logger.store_yaml(_sanitise_config(config))

    except Exception as e:
        status = "failed"
        error = e
        print(f"[Simulation] Failed: {e}")
        try:
            logger.store_yaml(_sanitise_config(config))
        except Exception:
            pass
        raise

    finally:
        end_time = time.time()
        elapsed_time = str(datetime.timedelta(seconds=round(end_time - start_time)))
        logger.store_run_details(
            timestamp,
            turn_counter,
            elapsed_time,
            seed=seed,
            successful=(status != "failed"),
            status=status,
            error=error,
        )