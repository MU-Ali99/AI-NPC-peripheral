from __future__ import annotations

import logging
import re
import time

from fastapi import FastAPI

from . import __version__
from .backends import LlmBackend, LlmBackendError, OllamaBackend
from .config import Settings
from .models import ConversationRequest, ConversationResponse
from .profiles import ProfileNotFoundError, ProfileStore
from .prompt import build_prompt

logger = logging.getLogger("npc_bridge")


def clean_dialogue(text: str, maximum: int) -> str:
    cleaned = re.sub(r"^(?:[A-Za-z ]+:\s*)", "", text.strip())
    cleaned = cleaned.strip('"“”')
    if len(cleaned) <= maximum:
        return cleaned
    shortened = cleaned[: maximum - 1].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{shortened}…"


def create_app(settings: Settings | None = None, backend: LlmBackend | None = None) -> FastAPI:
    settings = settings or Settings.load()
    backend = backend or OllamaBackend(settings.ollama_endpoint, settings.ollama_model, settings.ollama_timeout_seconds)
    profiles = ProfileStore(settings.profiles_path)
    api = FastAPI(title="NPCBridge", version=__version__)

    @api.get("/health")
    async def health() -> dict:
        return {"status": "ok", "version": __version__, "backend": type(backend).__name__}

    @api.post("/v1/conversation", response_model=ConversationResponse)
    @api.post("/conversation", response_model=ConversationResponse, include_in_schema=False)
    async def conversation(request: ConversationRequest) -> ConversationResponse:
        started = time.perf_counter()
        logger.info("Request received game=%s npc=%s", request.game, request.npc.id)
        try:
            profile = profiles.load(request.game, request.npc.id)
            system, user = build_prompt(request, profile)
            logger.info("Calling model npc=%s", request.npc.id)
            dialogue = clean_dialogue(await backend.generate(system, user), settings.maximum_characters)
            logger.info("Request completed npc=%s elapsed_ms=%d", request.npc.id, (time.perf_counter() - started) * 1000)
            return ConversationResponse(success=True, npc=request.npc.displayName, dialogue=dialogue)
        except ProfileNotFoundError as exc:
            logger.warning("Profile unavailable npc=%s", request.npc.id)
            return ConversationResponse(success=False, npc=request.npc.displayName, error=str(exc))
        except LlmBackendError as exc:
            logger.error("Model call failed npc=%s: %s", request.npc.id, exc)
            return ConversationResponse(success=False, npc=request.npc.displayName, error=str(exc))

    return api


app = create_app()

