from __future__ import annotations

import logging
import sqlite3
import time
from fastapi import FastAPI
from . import __version__
from .backends import LlmBackend, LlmBackendError, OllamaBackend
from .config import Settings
from .models import ConversationRequestV1, ConversationRequestV2, ConversationResponseV1, ConversationResponseV2, ExtendedContext, GameIdentity, NpcIdentity, PlayerIdentity, RelationshipContext, WorldContextV2
from .memory import MemoryStore
from .persona import PersonaEngine
from .profiles import InvalidProfileError, ProfileNotFoundError, ProfileStore

logger = logging.getLogger("npc_bridge")

def translate_v1(request: ConversationRequestV1) -> ConversationRequestV2:
    return ConversationRequestV2(
        game=GameIdentity(id=request.game, name="Stardew Valley"),
        npc=NpcIdentity(id=request.npc.id, displayName=request.npc.displayName, profileId=f"{request.game}.{request.npc.id.lower()}"),
        player=PlayerIdentity(id="player", displayName=request.player.name, message=request.player.message),
        relationship=RelationshipContext(level=request.npc.friendshipHearts, label="friendship_hearts"),
        world=WorldContextV2(location=request.world.location, time=request.world.time, day=request.world.day, season=request.world.season, weather=request.world.weather),
        context=ExtendedContext()
    )

def create_app(settings: Settings | None = None, backend: LlmBackend | None = None) -> FastAPI:
    settings = settings or Settings.load()
    backend = backend or OllamaBackend(settings.ollama_endpoint, settings.ollama_model, settings.ollama_timeout_seconds)
    profiles = ProfileStore(settings.profiles_path)
    persona = PersonaEngine(backend, settings.maximum_characters)
    memory = MemoryStore(settings.memory_path, settings.initial_relationship_score)
    api = FastAPI(title="NPCBridge", version=__version__)

    @api.get("/health")
    async def health() -> dict:
        return {"status": "ok", "version": __version__, "backend": type(backend).__name__, "protocols": ["1.0", "2.0"]}

    async def run(request: ConversationRequestV2) -> ConversationResponseV2:
        started = time.perf_counter()
        logger.info("Request received game=%s npc=%s profile=%s", request.game.id, request.npc.id, request.npc.profileId)
        try:
            profile = profiles.load(request.npc.profileId)
            before = memory.snapshot(request.game.id, request.player.id, request.npc.id)
            try:
                interaction_id = memory.begin(request.interactionId, request.game.id, request.player.id, request.npc.id, request.player.message, before)
            except sqlite3.IntegrityError:
                return ConversationResponseV2(success=False,npc=request.npc.displayName,
                    interactionId=request.interactionId,errorCode="duplicate_interaction",
                    error="This interaction ID has already been used.")
            try:
                result = await persona.respond(request, profile, before, memory.history(
                    request.game.id, request.player.id, request.npc.id, settings.recent_history_limit))
            except Exception:
                memory.mark(interaction_id, "FAILED", "model_failure")
                raise
            after = memory.finish(interaction_id, result.dialogue, result.sentiment,
                                  result.facialExpression, settings.sentiment_deltas)
            if after is None:
                return ConversationResponseV2(success=False,npc=request.npc.displayName,
                    interactionId=interaction_id,errorCode="interaction_not_committed",
                    error="The interaction was cancelled, duplicated, or superseded.")
            delta=after.score-before.score
            logger.info("Request completed npc=%s elapsed_ms=%d", request.npc.id, (time.perf_counter() - started) * 1000)
            return ConversationResponseV2(
                success=True, npc=request.npc.displayName, dialogue=result.dialogue,
                facialExpression=result.facialExpression, sentiment=result.sentiment,
                interactionId=interaction_id, relationshipDelta=delta,
                relationshipReason=f"Model judged the message {result.sentiment.lower()}.",
                memoryState=after.state, relationshipScore=after.score, relationshipState=after.state,
            )
        except ProfileNotFoundError as exc:
            return ConversationResponseV2(success=False, npc=request.npc.displayName, errorCode="profile_not_found", error=str(exc))
        except InvalidProfileError as exc:
            return ConversationResponseV2(success=False, npc=request.npc.displayName, errorCode="invalid_profile", error=str(exc))
        except LlmBackendError as exc:
            logger.error("Model call failed npc=%s: %s", request.npc.id, exc)
            return ConversationResponseV2(success=False, npc=request.npc.displayName, errorCode="backend_error", error=str(exc))

    @api.post("/v2/conversation", response_model=ConversationResponseV2)
    async def conversation_v2(request: ConversationRequestV2) -> ConversationResponseV2:
        return await run(request)

    @api.delete("/v2/interactions/{interaction_id}")
    async def cancel_interaction(interaction_id: str) -> dict:
        return {"interactionId": interaction_id, "cancelled": memory.mark(interaction_id, "CANCELLED")}

    @api.post("/v1/conversation", response_model=ConversationResponseV1)
    @api.post("/conversation", response_model=ConversationResponseV1, include_in_schema=False)
    async def conversation_v1(request: ConversationRequestV1) -> ConversationResponseV1:
        result = await run(translate_v1(request))
        return ConversationResponseV1(success=result.success, npc=result.npc, dialogue=result.dialogue, error=result.error)

    return api

app = create_app()
