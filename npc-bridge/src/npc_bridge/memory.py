from __future__ import annotations

import sqlite3
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path

STATES = ((850,"VERY_CLOSE"),(750,"TRUSTING"),(650,"WARM"),(550,"FRIENDLY"),(450,"NEUTRAL"),(400,"ANNOYED"),(300,"OFFENDED"),(200,"VERY_NEGATIVE"),(0,"HOSTILE"))

def relationship_state(score: int) -> str:
    return next(label for minimum, label in STATES if score >= minimum)

@dataclass(frozen=True)
class RelationshipSnapshot:
    score: int
    state: str
    version: int
    interaction_count: int

@dataclass(frozen=True)
class HistoryTurn:
    player_message: str
    npc_dialogue: str
    sentiment: str
    score_after: int

class MemoryStore:
    """Authoritative transactional relationship and conversation storage."""
    def __init__(self, path: Path, initial_score: int = 500):
        if str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self.initial_score = initial_score
        self.connection = sqlite3.connect(str(path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self._migrate()

    def _migrate(self) -> None:
        with self.lock, self.connection:
            columns = self.connection.execute("PRAGMA table_info(interactions)").fetchall()
            if columns and "interaction_id" not in {row[1] for row in columns}:
                self.connection.execute("ALTER TABLE interactions RENAME TO legacy_interactions")
            self.connection.executescript("""
                CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
                INSERT INTO schema_version(version) SELECT 2 WHERE NOT EXISTS(SELECT 1 FROM schema_version);
                CREATE TABLE IF NOT EXISTS npc_relationship_state(
                    game_id TEXT NOT NULL, player_id TEXT NOT NULL, npc_id TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 1000),
                    relationship_state TEXT NOT NULL, interaction_count INTEGER NOT NULL DEFAULT 0,
                    version INTEGER NOT NULL DEFAULT 0, last_interaction_at TEXT,
                    PRIMARY KEY(game_id, player_id, npc_id));
                CREATE TABLE IF NOT EXISTS interactions(
                    interaction_id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL, player_id TEXT NOT NULL, npc_id TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PENDING','COMPLETED','CANCELLED','FAILED','SUPERSEDED')),
                    player_message TEXT NOT NULL, npc_dialogue TEXT, model_sentiment TEXT, facial_expression TEXT,
                    score_before INTEGER NOT NULL, relationship_delta INTEGER, score_after INTEGER,
                    state_before TEXT NOT NULL, state_after TEXT, request_version INTEGER NOT NULL,
                    error_code TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, completed_at TEXT);
                CREATE INDEX IF NOT EXISTS ix_interactions_history
                ON interactions(game_id,player_id,npc_id,status,created_at DESC);
            """)
            self._import_legacy()

    def _import_legacy(self) -> None:
        if not self.connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='legacy_interactions'").fetchone():
            return
        running: dict[tuple[str,str,str], int] = {}
        counts: dict[tuple[str,str,str], int] = {}
        for row in self.connection.execute("SELECT * FROM legacy_interactions ORDER BY id").fetchall():
            iid = f"legacy-{row['id']}"
            if self.connection.execute("SELECT 1 FROM interactions WHERE interaction_id=?", (iid,)).fetchone():
                continue
            key = (row["game_id"],row["player_id"],row["npc_id"])
            before = running.get(key,self.initial_score)
            delta = int(row["relationship_delta"])
            after = max(0,min(1000,before+delta))
            sentiment = "POSITIVE" if delta > 0 else "NEGATIVE" if delta < 0 else "NEUTRAL"
            self.connection.execute("""INSERT INTO interactions(
                interaction_id,game_id,player_id,npc_id,status,player_message,npc_dialogue,model_sentiment,
                score_before,relationship_delta,score_after,state_before,state_after,request_version,created_at,completed_at)
                VALUES(?,?,?,?, 'COMPLETED',?,'',?,?,?,?,?,?,?,?,?)""",
                (iid,*key,row["message_excerpt"],sentiment,before,delta,after,relationship_state(before),
                 relationship_state(after),counts.get(key,0),row["created_at"],row["created_at"]))
            running[key],counts[key] = after,counts.get(key,0)+1
        for key,score in running.items():
            count=counts[key]
            self.connection.execute("""INSERT INTO npc_relationship_state
                (game_id,player_id,npc_id,score,relationship_state,interaction_count,version,last_interaction_at)
                VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(game_id,player_id,npc_id) DO NOTHING""",
                (*key,score,relationship_state(score),count,count))

    def snapshot(self, game_id: str, player_id: str, npc_id: str) -> RelationshipSnapshot:
        with self.lock:
            row=self.connection.execute("""SELECT score,relationship_state,version,interaction_count
                FROM npc_relationship_state WHERE game_id=? AND player_id=? AND npc_id=?""",(game_id,player_id,npc_id)).fetchone()
        return RelationshipSnapshot(self.initial_score,relationship_state(self.initial_score),0,0) if row is None else RelationshipSnapshot(*row)

    def history(self, game_id: str, player_id: str, npc_id: str, limit: int = 6) -> list[HistoryTurn]:
        with self.lock:
            rows=self.connection.execute("""SELECT player_message,npc_dialogue,model_sentiment,score_after FROM interactions
                WHERE game_id=? AND player_id=? AND npc_id=? AND status='COMPLETED'
                ORDER BY completed_at DESC,rowid DESC LIMIT ?""",(game_id,player_id,npc_id,limit)).fetchall()
        return [HistoryTurn(row[0],row[1] or "",row[2] or "NEUTRAL",row[3]) for row in reversed(rows)]

    def begin(self, interaction_id: str | None, game_id: str, player_id: str, npc_id: str, message: str, snapshot: RelationshipSnapshot) -> str:
        iid=interaction_id or str(uuid.uuid4())
        with self.lock,self.connection:
            self.connection.execute("""INSERT INTO interactions(interaction_id,game_id,player_id,npc_id,status,
                player_message,score_before,state_before,request_version) VALUES(?,?,?,?, 'PENDING',?,?,?,?)""",
                (iid,game_id,player_id,npc_id,message,snapshot.score,snapshot.state,snapshot.version))
        return iid

    def finish(self, interaction_id: str, dialogue: str, sentiment: str, expression: str, deltas: dict[str,int]) -> RelationshipSnapshot | None:
        delta=deltas[sentiment]
        with self.lock,self.connection:
            row=self.connection.execute("SELECT * FROM interactions WHERE interaction_id=?",(interaction_id,)).fetchone()
            if row is None or row["status"]!="PENDING":
                return None
            current=self.snapshot(row["game_id"],row["player_id"],row["npc_id"])
            if current.version!=row["request_version"]:
                self.connection.execute("UPDATE interactions SET status='SUPERSEDED',completed_at=CURRENT_TIMESTAMP WHERE interaction_id=?",(interaction_id,))
                return None
            after=max(0,min(1000,current.score+delta))
            state=relationship_state(after)
            self.connection.execute("""INSERT INTO npc_relationship_state
                (game_id,player_id,npc_id,score,relationship_state,interaction_count,version,last_interaction_at)
                VALUES(?,?,?,?,?,1,1,CURRENT_TIMESTAMP) ON CONFLICT(game_id,player_id,npc_id) DO UPDATE SET
                score=excluded.score,relationship_state=excluded.relationship_state,interaction_count=interaction_count+1,
                version=version+1,last_interaction_at=CURRENT_TIMESTAMP""",(row["game_id"],row["player_id"],row["npc_id"],after,state))
            self.connection.execute("""UPDATE interactions SET status='COMPLETED',npc_dialogue=?,model_sentiment=?,
                facial_expression=?,relationship_delta=?,score_after=?,state_after=?,completed_at=CURRENT_TIMESTAMP
                WHERE interaction_id=? AND status='PENDING'""",(dialogue,sentiment,expression,delta,after,state,interaction_id))
            return RelationshipSnapshot(after,state,current.version+1,current.interaction_count+1)

    def mark(self, interaction_id: str, status: str, error_code: str | None=None) -> bool:
        if status not in {"CANCELLED","FAILED"}:
            raise ValueError("Invalid terminal status")
        with self.lock,self.connection:
            cursor=self.connection.execute("""UPDATE interactions SET status=?,error_code=?,completed_at=CURRENT_TIMESTAMP
                WHERE interaction_id=? AND status='PENDING'""",(status,error_code,interaction_id))
            return cursor.rowcount==1
