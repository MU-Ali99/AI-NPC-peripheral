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
    ollama_model: str = "qwen2.5:1.5b"
    ollama_timeout_seconds: float = 75
    maximum_characters: int = 400
    profiles_path: Path = project_root() / "npc-profiles"
    memory_path: Path = project_root() / "data" / "npcbridge.db"

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
        )
