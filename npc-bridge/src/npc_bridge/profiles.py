from __future__ import annotations

import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class ProfileNotFoundError(Exception):
    pass

class InvalidProfileError(Exception):
    pass

class IdentityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    game: str
    description: str = ""

class PersonalityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    traits: list[str] = Field(default_factory=list)
    tone: list[str] = Field(default_factory=list)
    behavior: list[str] = Field(default_factory=list)

class SpeechProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cadence: str = "natural and concise"
    vocabulary: list[str] = Field(default_factory=list)
    verbalHabits: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    reactions: dict[str, list[str]] = Field(default_factory=dict)

class KnowledgeProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gameWorld: list[str] = Field(default_factory=list)
    generalKnowledge: bool = True
    boundaries: list[str] = Field(default_factory=list)

class PersonaBoundaries(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stayInCharacter: bool = True
    neverMentionAI: bool = True
    rules: list[str] = Field(default_factory=list)

class NpcProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    identity: IdentityProfile
    personality: PersonalityProfile
    speech: SpeechProfile = Field(default_factory=SpeechProfile)
    knowledge: KnowledgeProfile = Field(default_factory=KnowledgeProfile)
    boundaries: PersonaBoundaries = Field(default_factory=PersonaBoundaries)
    maximumCharacters: int = Field(default=400, ge=40, le=2000)

class ProfileStore:
    def __init__(self, root: Path):
        self.root = root

    def load(self, profile_id: str) -> NpcProfile:
        for path in self.root.rglob("*.json"):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if raw.get("id") != profile_id:
                continue
            try:
                return NpcProfile.model_validate(raw)
            except ValidationError as exc:
                raise InvalidProfileError(f"Profile '{profile_id}' is invalid.") from exc
        raise ProfileNotFoundError(f"No NPC profile is available for '{profile_id}'.")
