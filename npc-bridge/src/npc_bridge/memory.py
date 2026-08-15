from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MemorySummary:
    recent_categories: tuple[str, ...]
    compliment_streak: int
    offense_score: int

    @property
    def state(self) -> str:
        if self.offense_score >= 60:
            return "holding_a_grudge"
        if self.offense_score >= 25:
            return "wary"
        if self.compliment_streak >= 3:
            return "suspicious_of_flattery"
        return "normal"


class MemoryStore:
    def __init__(self, path: Path):
        if str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path), check_same_thread=False)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL, player_id TEXT NOT NULL, npc_id TEXT NOT NULL,
            category TEXT NOT NULL, relationship_delta INTEGER NOT NULL,
            message_excerpt TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        self.connection.commit()

    def summary(self, game_id: str, player_id: str, npc_id: str) -> MemorySummary:
        rows = self.connection.execute(
            "SELECT category, relationship_delta FROM interactions WHERE game_id=? AND player_id=? AND npc_id=? ORDER BY id DESC LIMIT 8",
            (game_id, player_id, npc_id),
        ).fetchall()
        categories = tuple(row[0] for row in rows)
        streak = 0
        for category in categories:
            if category != "compliment":
                break
            streak += 1
        offense = min(100, sum(abs(row[1]) for row in rows if row[0] in {"rude", "hostile"}))
        return MemorySummary(categories, streak, offense)

    def record(self, game_id: str, player_id: str, npc_id: str, category: str, delta: int, message: str) -> None:
        self.connection.execute(
            "INSERT INTO interactions(game_id, player_id, npc_id, category, relationship_delta, message_excerpt) VALUES(?,?,?,?,?,?)",
            (game_id, player_id, npc_id, category, delta, message[:160]),
        )
        self.connection.commit()


class RelationshipEngine:
    compliment_terms = (
        "beautiful", "pretty", "handsome", "amazing", "wonderful", "love you",
        "you are kind", "you're kind", "kind person", "you are nice", "you're nice",
        "good person", "great person", "proud of you", "admire you", "the best",
    )
    hostile_terms = ("fuck you", "hate you", "kill you", "worthless", "piece of shit")
    rude_terms = ("stupid", "idiot", "moron", "old fart", "brat", "loser", "shut up")

    @classmethod
    def classify(cls, message: str, model_tone: str) -> str:
        lowered = message.lower()
        if any(term in lowered for term in cls.hostile_terms) or model_tone == "hostile":
            return "hostile"
        if any(term in lowered for term in cls.rude_terms) or model_tone == "rude":
            return "rude"
        if any(term in lowered for term in cls.compliment_terms) or model_tone == "compliment":
            return "compliment"
        return model_tone if model_tone in {"friendly", "flirty", "uncomfortable"} else "neutral"

    @staticmethod
    def impact(category: str, memory: MemorySummary) -> tuple[int, str]:
        if category == "compliment":
            if memory.compliment_streak >= 3:
                return -2, "Repeated praise feels forced and makes the character uncomfortable."
            if memory.compliment_streak == 2:
                return 0, "The praise is becoming repetitive and no longer feels sincere."
            if memory.compliment_streak == 1:
                return 3, "The compliment is appreciated, but repeated praise has less impact."
            return 8, "A sincere compliment improves the relationship."
        if category == "friendly":
            return 2, "A friendly exchange slightly improves the relationship."
        if category == "flirty":
            return (2, "The attention is received cautiously.")
        if category == "rude":
            penalty = -12 if memory.offense_score < 25 else -18
            return penalty, "The insult damages trust and may be remembered."
        if category == "hostile":
            penalty = -25 if memory.offense_score < 25 else -35
            return penalty, "Hostility seriously damages trust and strengthens the grudge."
        if category == "uncomfortable":
            return -3, "The exchange makes the character uncomfortable."
        return 0, "The conversation does not change the relationship."
