from __future__ import annotations

from abc import ABC, abstractmethod
import logging
import time
from typing import Any

import httpx

logger = logging.getLogger("npc_bridge")


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

    async def warmup(self) -> None:
        started=time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response=await client.post(f"{self.endpoint}/api/generate",json={
                    "model":self.model,"prompt":"","stream":False,"keep_alive":"30m",
                    "options":{"num_ctx":3072,"num_predict":1},
                })
                response.raise_for_status()
            logger.info("Ollama model preloaded model=%s elapsed_ms=%d",self.model,(time.perf_counter()-started)*1000)
        except httpx.HTTPError as exc:
            logger.warning("Ollama preload failed; first conversation will load the model: %s",exc)

    async def generate(self, system: str, user: str, output_schema: dict[str, Any] | None = None) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "keep_alive": "30m",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0.35, "num_predict": 140, "num_ctx": 3072},
        }
        if output_schema is not None:
            payload["format"] = output_schema
        try:
            started = time.perf_counter()
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{self.endpoint}/api/chat", json=payload)
                if response.status_code == 400 and output_schema is not None:
                    # Some Ollama/model combinations support JSON mode but can't
                    # compile every JSON schema into a grammar. Validation still
                    # happens in PersonaEngine, so fall back without leaking text.
                    payload["format"] = "json"
                    response = await client.post(f"{self.endpoint}/api/chat", json=payload)
                response.raise_for_status()
                result = response.json()
                text = result["message"]["content"]
                logger.info(
                    "Ollama completed model=%s elapsed_ms=%d load_ms=%d prompt_tokens=%s prompt_ms=%d output_tokens=%s output_ms=%d",
                    self.model,
                    (time.perf_counter() - started) * 1000,
                    result.get("load_duration", 0) / 1_000_000,
                    result.get("prompt_eval_count"),
                    result.get("prompt_eval_duration", 0) / 1_000_000,
                    result.get("eval_count"),
                    result.get("eval_duration", 0) / 1_000_000,
                )
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise LlmBackendError("The local language model is unavailable or returned an invalid response.") from exc
        if not text or not text.strip():
            raise LlmBackendError("The local language model returned an empty response.")
        return text.strip()
