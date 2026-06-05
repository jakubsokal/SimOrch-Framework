import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import json
import asyncio
from fastapi.responses import StreamingResponse
from ..services.simulation_service import run_simulation
from ..llm.requirements_enum import PROVIDER_REQUIREMENTS
from ..llm.llm_provider_keys import PROVIDER_API_KEY_ENV
from .key_validator import validate_provider_key
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

router = APIRouter(prefix="/initiate", tags=["initiate"])
simulation_status = {"status": "idle"}


@router.get("/env-keys")
async def get_env_key_status() -> Dict[str, bool]:
    result = {}
    for provider, env_var in PROVIDER_API_KEY_ENV.items():
        if env_var is None:
            result[provider.lower()] = True
        else:
            key = os.getenv(env_var)
            result[provider.lower()] = bool(key and key.strip())
    return result


@router.post("/")
async def initiate_simulation(config: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
    if "scenario" not in config or "scenarioTruths" not in config or "re_agents" not in config or "user_agents" not in config:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: scenario, scenarioTruths, re_agents, user_agents"
        )

    all_agents = (
        config.get("re_agents", []) +
        config.get("user_agents", []) +
        ([config.get("helper_agent")] if config.get("helper_agent") else [])
    )

    for agent in all_agents:
        if not agent:
            continue
        provider = agent.get("provider", "").upper()
        requirements = PROVIDER_REQUIREMENTS.get(provider, {})

        if requirements.get("requires_api_key"):
            env_var = PROVIDER_API_KEY_ENV.get(provider)
            env_key = os.getenv(env_var) if env_var else None
            ui_key = agent.get("api_key", "").strip() if isinstance(agent.get("api_key"), str) else ""
            effective_key = env_key or ui_key

            if not effective_key:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider '{provider}' requires an API key. Set {env_var} in your .env or supply it in the request."
                )

            # only validate UI-supplied keys, .env keys are trusted
            if ui_key and not env_key:
                await validate_provider_key(provider, ui_key)

    simulation_status["status"] = "running"
    background_tasks.add_task(run_and_update, config)
    return {"message": "Simulation initiated successfully"}


async def run_and_update(config: dict):
    try:
        await asyncio.to_thread(run_simulation, config)
        simulation_status["status"] = "completed"
    except Exception as e:
        simulation_status["status"] = "failed"
        simulation_status["error"] = str(e)
        print(f"[Simulation] Failed: {e}")


@router.get("/stream")
async def stream_status():
    async def event_generator():
        while True:
            payload = {"status": simulation_status["status"]}
            if simulation_status["status"] == "failed":
                payload["error"] = simulation_status.get("error", "Unknown error")
            data = json.dumps(payload)
            yield f"data: {data}\n\n"
            print(f"[Stream] Sent status update: {data}")
            if simulation_status["status"] in ("completed", "failed"):
                simulation_status["status"] = "idle"
                simulation_status.pop("error", None)
                break
            await asyncio.sleep(10)

    return StreamingResponse(event_generator(), media_type="text/event-stream")