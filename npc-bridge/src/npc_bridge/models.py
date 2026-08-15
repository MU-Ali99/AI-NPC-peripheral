from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class V1NpcContext(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    displayName: str = Field(min_length=1, max_length=80)
    friendshipHearts: int = Field(default=0, ge=0, le=14)

class V1WorldContext(StrictModel):
    location: str = Field(min_length=1, max_length=120)
    season: str = Field(min_length=1, max_length=40)
    day: int = Field(ge=1, le=366)
    time: int = Field(ge=0, le=3000)
    weather: str = Field(min_length=1, max_length=80)

class V1PlayerContext(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)

class ConversationRequestV1(StrictModel):
    protocolVersion: Literal["1.0"] = "1.0"
    game: Literal["stardew_valley"]
    npc: V1NpcContext
    world: V1WorldContext
    player: V1PlayerContext

class ConversationResponseV1(StrictModel):
    protocolVersion: Literal["1.0"] = "1.0"
    success: bool
    npc: str
    dialogue: str = ""
    error: str | None = None

class GameIdentity(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]{0,79}$")
    name: str | None = Field(default=None, max_length=120)

class NpcIdentity(StrictModel):
    id: str = Field(min_length=1, max_length=120)
    displayName: str = Field(min_length=1, max_length=120)
    profileId: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]{0,159}$")

class PlayerIdentity(StrictModel):
    id: str = Field(default="player", min_length=1, max_length=120)
    displayName: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=1000)

class RelationshipContext(StrictModel):
    level: float | None = Field(default=None, ge=-1000, le=1000)
    label: str | None = Field(default=None, max_length=80)
    custom: dict[str, Any] = Field(default_factory=dict)

class WorldContextV2(StrictModel):
    location: str | None = Field(default=None, max_length=160)
    time: str | int | None = None
    day: int | str | None = None
    season: str | None = Field(default=None, max_length=80)
    weather: str | None = Field(default=None, max_length=80)
    custom: dict[str, Any] = Field(default_factory=dict)

class ExtendedContext(StrictModel):
    nearbyCharacters: list[dict[str, Any]] = Field(default_factory=list, max_length=30)
    recentEvents: list[dict[str, Any] | str] = Field(default_factory=list, max_length=30)
    questState: dict[str, Any] = Field(default_factory=dict)
    custom: dict[str, Any] = Field(default_factory=dict)

class ConversationRequestV2(StrictModel):
    protocolVersion: Literal["2.0"] = "2.0"
    game: GameIdentity
    npc: NpcIdentity
    player: PlayerIdentity
    relationship: RelationshipContext | None = None
    world: WorldContextV2 | None = None
    context: ExtendedContext = Field(default_factory=ExtendedContext)
    interactionId: str | None = Field(default=None, min_length=8, max_length=80)

class ConversationResponseV2(StrictModel):
    protocolVersion: Literal["2.0"] = "2.0"
    success: bool
    npc: str
    dialogue: str = ""
    emotion: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    facialExpression: str | None = None
    relationshipDelta: int = Field(default=0, ge=-100, le=100)
    relationshipReason: str | None = None
    memoryState: str | None = None
    interactionId: str | None = None
    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE"] | None = None
    relationshipScore: int | None = Field(default=None, ge=0, le=1000)
    relationshipState: str | None = None
    errorCode: str | None = None
    error: str | None = None

class ModelDialogue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dialogue: str = Field(min_length=1, max_length=2000)
    facialExpression: str = Field(default="neutral", min_length=1, max_length=120)
    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE"]
