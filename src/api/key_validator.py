import httpx
from fastapi import HTTPException

VALIDATION_ENDPOINTS = {
    "OPENAI": {
        "method": "GET",
        "url": "https://api.openai.com/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "body": None,
    },
    "ANTHROPIC": {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "headers": lambda key: {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        "body": {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}],
        },
    },
    "GROQ": {
        "method": "GET",
        "url": "https://api.groq.com/openai/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "body": None,
    },
    "GEMINI": {
        "method": "GET",
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "headers": lambda key: {},
        "params": lambda key: {"key": key},
        "body": None,
    },
}


async def validate_provider_key(provider: str, api_key: str):
    config = VALIDATION_ENDPOINTS.get(provider)
    if not config:
        return  # unknown provider, skip

    headers = config["headers"](api_key)
    params = config.get("params", lambda k: {})(api_key)
    body = config.get("body")

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            if config["method"] == "GET":
                response = await client.get(config["url"], headers=headers, params=params)
            else:
                response = await client.post(config["url"], headers=headers, json=body)

        # 401 = bad key, 403 = valid key but no permission (still valid)
        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid API key for {provider.capitalize()}. Please check the key and try again."
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail=f"Could not reach {provider.capitalize()} to validate the API key. Check your connection."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error validating {provider.capitalize()} key: {str(e)}"
        )