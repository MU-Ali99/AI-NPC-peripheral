from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    bridge_host: str = "127.0.0.1"
    bridge_port: int = 8765
    ollama_endpoint: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b-instruct-2507-q4_K_M"
    ollama_timeout_seconds: float = 75
    maximum_characters: int = 400
    profiles_path: Path = project_root() / "npc-profiles"
    memory_path: Path = project_root() / "data" / "npcbridge.db"
    initial_relationship_score: int = 500
    positive_delta: int = 10
    neutral_delta: int = 0
    negative_delta: int = -10
    recent_history_limit: int = 6

    @property
    def sentiment_deltas(self) -> dict[str, int]:
        return {"POSITIVE": self.positive_delta, "NEUTRAL": self.neutral_delta, "NEGATIVE": self.negative_delta}

    @classmethod
    def load(cls) -> "Settings":
        config_path = Path(os.getenv("NPCBRIDGE_CONFIG", project_root() / "config" / "default.json"))
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return cls(
            bridge_host=os.getenv("NPCBRIDGE_HOST", data["bridge"]["host"]),
            bridge_port=int(os.getenv("NPCBRIDGE_PORT", data["bridge"]["port"])),
            ollama_endpoint=os.getenv("NPCBRIDGE_OLLAMA_ENDPOINT", data["ollama"]["endpoint"]),
            ollama_model=os.getenv("NPCBRIDGE_MODEL", data["ollama"]["model"]),
            ollama_timeout_seconds=float(data["ollama"]["timeoutSeconds"]),
            maximum_characters=int(data["dialogue"]["maximumCharacters"]),
            profiles_path=Path(os.getenv("NPCBRIDGE_PROFILES", project_root() / "npc-profiles")),
            memory_path=Path(os.getenv("NPCBRIDGE_MEMORY", project_root() / "data" / "npcbridge.db")),
            initial_relationship_score=int(data.get("relationship", {}).get("initialScore", 500)),
            positive_delta=int(data.get("relationship", {}).get("positiveDelta", 10)),
            neutral_delta=int(data.get("relationship", {}).get("neutralDelta", 0)),
            negative_delta=int(data.get("relationship", {}).get("negativeDelta", -10)),
            recent_history_limit=int(data.get("memory", {}).get("recentHistoryLimit", 6)),
        )
