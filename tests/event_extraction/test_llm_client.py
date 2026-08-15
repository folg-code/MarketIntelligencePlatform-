"""Unit tests for the Ollama LLM client adapter.

Uses `httpx.MockTransport` (no live Ollama call) per the project's testing
policy and `docs/architecture/ai-and-evidence.md` (Testing Expectations).
"""

from __future__ import annotations

import json

import httpx
import pytest

from market_intel.event_extraction.llm_client import (
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_MODEL,
    OLLAMA_BASE_URL_ENV_VAR,
    OLLAMA_MODEL_ENV_VAR,
    OllamaClient,
)


def test_model_name_defaults_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(OLLAMA_MODEL_ENV_VAR, raising=False)

    client = OllamaClient()

    assert client.model_name == DEFAULT_OLLAMA_MODEL


def test_model_name_reads_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(OLLAMA_MODEL_ENV_VAR, "custom-model")

    client = OllamaClient()

    assert client.model_name == "custom-model"


def test_explicit_model_argument_overrides_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(OLLAMA_MODEL_ENV_VAR, "env-model")

    client = OllamaClient(model="explicit-model")

    assert client.model_name == "explicit-model"


async def test_generate_posts_to_configured_base_url_and_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(OLLAMA_BASE_URL_ENV_VAR, "http://example-ollama:11434")
    monkeypatch.setenv(OLLAMA_MODEL_ENV_VAR, "test-model")

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"response": "the raw completion"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OllamaClient(http_client=http_client)
        result = await client.generate(system_prompt="system", user_prompt="user")

    assert result == "the raw completion"
    assert len(requests) == 1
    assert str(requests[0].url) == "http://example-ollama:11434/api/generate"
    body = json.loads(requests[0].content)
    assert body == {
        "model": "test-model",
        "prompt": "user",
        "system": "system",
        "stream": False,
    }


async def test_generate_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="internal error")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OllamaClient(http_client=http_client)
        with pytest.raises(httpx.HTTPStatusError):
            await client.generate(system_prompt="system", user_prompt="user")


def test_default_base_url_is_local_ollama_standard_address() -> None:
    assert DEFAULT_OLLAMA_BASE_URL == "http://localhost:11434"
