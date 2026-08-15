"""LLM client adapter interface and local Ollama implementation.

Event extraction reaches the LLM only through this adapter (per project
convention: external systems reached through adapters/interfaces, not
called directly from business logic; see `docs/architecture/overview.md`).
`LLMClient` is provider-agnostic so a future provider could implement it,
even though only a local Ollama instance is implemented for the MVP per
`docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

import httpx

OLLAMA_BASE_URL_ENV_VAR = "OLLAMA_BASE_URL"
OLLAMA_MODEL_ENV_VAR = "OLLAMA_MODEL"

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
# No specific model is designated by ADR-002; this is a placeholder default
# only. Operators must set OLLAMA_MODEL to whatever model they have pulled
# locally (see ImplementationReport.assumptions).
DEFAULT_OLLAMA_MODEL = "llama3.1"

OLLAMA_REQUEST_TIMEOUT_SECONDS = 120.0


class LLMClient(ABC):
    """Adapter interface for a text-completion LLM used by event extraction."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the underlying model, recorded for basic traceability."""

    @abstractmethod
    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        """Return the raw text completion for the given prompt pair."""


class OllamaClient(LLMClient):
    """`LLMClient` backed by a local Ollama instance's REST API (`/api/generate`).

    Base URL and model are read from the `OLLAMA_BASE_URL`/`OLLAMA_MODEL`
    environment variables (never hardcoded), so the target instance and
    model are operator-configurable without a code change.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = (
            base_url or os.environ.get(OLLAMA_BASE_URL_ENV_VAR) or DEFAULT_OLLAMA_BASE_URL
        ).rstrip("/")
        self._model = model or os.environ.get(OLLAMA_MODEL_ENV_VAR) or DEFAULT_OLLAMA_MODEL
        self._http_client = http_client

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
        }

        if self._http_client is not None:
            response = await self._http_client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()["response"]

        async with httpx.AsyncClient(timeout=OLLAMA_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()["response"]
