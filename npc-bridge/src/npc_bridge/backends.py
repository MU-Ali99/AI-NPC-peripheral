from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx


class LlmBackendError(Exception):
    pass


class LlmBackend(ABC):
    @abstractmethod
    async def generate(self, system: str, user: str, output_schema: dict[str, Any] | None = None) -> str:
        raise NotImplementedError


class OllamaBackend(LlmBackend):
    def __init__(self, endpoint: str, model: str, timeout_seconds: float):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def generate(self, system: str, user: str, output_schema: dict[str, Any] | None = None) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0.35, "num_predict": 240, "num_ctx": 4096},
        }
        if output_schema is not None:
            payload["format"] = output_schema
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{self.endpoint}/api/chat", json=payload)
                if response.status_code == 400 and output_schema is not None:
                    # Some Ollama/model combinations support JSON mode but can't
                    # compile every JSON schema into a grammar. Validation still
                    # happens in PersonaEngine, so fall back without leaking text.
                    payload["format"] = "json"
                    response = await client.post(f"{self.endpoint}/api/chat", json=payload)
                response.raise_for_status()
                text = response.json()["message"]["content"]
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise LlmBackendError("The local language model is unavailable or returned an invalid response.") from exc
        if not text or not text.strip():
            raise LlmBackendError("The local language model returned an empty response.")
        return text.strip()
