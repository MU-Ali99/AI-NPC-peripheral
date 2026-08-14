from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NpcContext(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    displayName: str = Field(min_length=1, max_length=80)
    friendshipHearts: int = Field(default=0, ge=0, le=14)


class WorldContext(StrictModel):
    location: str = Field(min_length=1, max_length=120)
    season: str = Field(min_length=1, max_length=20)
    day: int = Field(ge=1, le=31)
    time: int = Field(ge=0, le=3000)
    weather: str = Field(min_length=1, max_length=40)


class PlayerContext(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)


class ConversationRequest(StrictModel):
    protocolVersion: Literal["1.0"] = "1.0"
    game: Literal["stardew_valley"]
    npc: NpcContext
    world: WorldContext
    player: PlayerContext


class ConversationResponse(StrictModel):
    protocolVersion: Literal["1.0"] = "1.0"
    success: bool
    npc: str
    dialogue: str = ""
    error: str | None = None

