from __future__ import annotations

import logging
import time
from fastapi import FastAPI
from . import __version__
from .backends import LlmBackend, LlmBackendError, OllamaBackend
from .config import Settings
from .models import ConversationRequestV1, ConversationRequestV2, ConversationResponseV1, ConversationResponseV2, ExtendedContext, GameIdentity, NpcIdentity, PlayerIdentity, RelationshipContext, WorldContextV2
from .memory import MemoryStore, RelationshipEngine
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
    memory = MemoryStore(settings.memory_path)
    api = FastAPI(title="NPCBridge", version=__version__)

    @api.get("/health")
    async def health() -> dict:
        return {"status": "ok", "version": __version__, "backend": type(backend).__name__, "protocols": ["1.0", "2.0"]}

    async def run(request: ConversationRequestV2) -> ConversationResponseV2:
        started = time.perf_counter()
        logger.info("Request received game=%s npc=%s profile=%s", request.game.id, request.npc.id, request.npc.profileId)
        try:
            profile = profiles.load(request.npc.profileId)
            before = memory.summary(request.game.id, request.player.id, request.npc.id)
            request.context.custom["relationshipMemory"] = {
                "state": before.state,
                "recentInteractionTypes": list(before.recent_categories),
                "complimentStreak": before.compliment_streak,
                "offenseScore": before.offense_score,
            }
            result = await persona.respond(request, profile)
            category = RelationshipEngine.classify(request.player.message, result.interactionTone)
            delta, reason = RelationshipEngine.impact(category, before)
            expression = result.facialExpression
            if expression.strip().lower() in {"neutral", "normal", "none"}:
                expression = {
                    "compliment": "a small, cautious smile",
                    "friendly": "a warm, attentive look",
                    "flirty": "a slightly uncertain smile",
                    "uncomfortable": "an uneasy, guarded look",
                    "rude": "a firm, offended frown",
                    "hostile": "an angry, distrustful glare",
                }.get(category, "a calm, observant expression")
            memory.record(request.game.id, request.player.id, request.npc.id, category, delta, request.player.message)
            after = memory.summary(request.game.id, request.player.id, request.npc.id)
            logger.info("Request completed npc=%s elapsed_ms=%d", request.npc.id, (time.perf_counter() - started) * 1000)
            return ConversationResponseV2(
                success=True, npc=request.npc.displayName, dialogue=result.dialogue,
                emotion=result.emotion, confidence=result.confidence,
                facialExpression=expression,
                relationshipDelta=delta, relationshipReason=reason, memoryState=after.state,
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

    @api.post("/v1/conversation", response_model=ConversationResponseV1)
    @api.post("/conversation", response_model=ConversationResponseV1, include_in_schema=False)
    async def conversation_v1(request: ConversationRequestV1) -> ConversationResponseV1:
        result = await run(translate_v1(request))
        return ConversationResponseV1(success=result.success, npc=result.npc, dialogue=result.dialogue, error=result.error)

    return api

app = create_app()
