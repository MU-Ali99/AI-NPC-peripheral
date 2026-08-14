import json
import re
from pathlib import Path


class ProfileNotFoundError(Exception):
    pass


class ProfileStore:
    def __init__(self, root: Path):
        self.root = root

    def load(self, game: str, npc_id: str) -> dict:
        safe_game = self._slug(game)
        safe_npc = self._slug(npc_id)
        path = self.root / safe_game / f"{safe_npc}.json"
        if not path.is_file():
            raise ProfileNotFoundError(f"No AI profile is available for {npc_id}.")
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9_-]", "", value.lower().replace(" ", "_"))

