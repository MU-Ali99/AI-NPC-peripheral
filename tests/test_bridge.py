import json
import sqlite3
from pathlib import Path
from typing import Any
import pytest
from fastapi.testclient import TestClient
from npc_bridge.app import create_app
from npc_bridge.backends import LlmBackend, LlmBackendError
from npc_bridge.config import Settings
from npc_bridge.memory import MemoryStore, relationship_state
from npc_bridge.models import ConversationRequestV2
from npc_bridge.persona import PersonaEngine
from npc_bridge.profiles import ProfileStore

class FakeBackend(LlmBackend):
    def __init__(self, sentiments: list[str]|None=None, malformed: bool=False):
        self.sentiments=sentiments or ["NEUTRAL"]
        self.calls=0
        self.malformed=malformed
        self.users:list[str]=[]
    async def generate(self, system: str, user: str, output_schema: dict[str,Any]|None=None)->str:
        assert "Judge only the CURRENT player message" in system
        assert output_schema and output_schema["additionalProperties"] is False
        self.users.append(user)
        self.calls+=1
        if self.malformed:
            return "not json"
        sentiment=self.sentiments[min(self.calls-1,len(self.sentiments)-1)]
        return json.dumps({"dialogue":f"A character-specific reply number {self.calls}.","sentiment":sentiment,"facialExpression":"a thoughtful frown"})

class BrokenBackend(LlmBackend):
    async def generate(self,*args,**kwargs)->str:
        raise LlmBackendError("offline")

def settings(path: Path=Path(":memory:"))->Settings:
    return Settings(profiles_path=Path(__file__).parents[1]/"npc-profiles",memory_path=path)

def payload(message: str="Hello.") -> dict:
    return {"protocolVersion":"2.0","game":{"id":"stardew_valley","name":"Stardew Valley"},
        "npc":{"id":"Linus","displayName":"Linus","profileId":"stardew_valley.linus"},
        "player":{"id":"player","displayName":"Player","message":message},
        "relationship":{"level":5,"label":"friendship_hearts"},
        "world":{"location":"Mountain","season":"Spring","day":1,"time":"07:40","weather":"clear"},
        "context":{"custom":{"adapterVersion":"test"}}}

def test_model_sentiment_controls_score_and_response() -> None:
    response=TestClient(create_app(settings(),FakeBackend(["POSITIVE"]))).post("/v2/conversation",json=payload()).json()
    assert response["success"] and response["relationshipDelta"]==10
    assert response["relationshipScore"]==510 and response["sentiment"]=="POSITIVE"
    assert response["relationshipState"]=="NEUTRAL" and response["interactionId"]

def test_negative_and_neutral_deltas_are_generic() -> None:
    backend=FakeBackend(["NEGATIVE","NEUTRAL"])
    client=TestClient(create_app(settings(),backend))
    assert client.post("/v2/conversation",json=payload("Anything")).json()["relationshipScore"]==490
    second=client.post("/v2/conversation",json=payload("Anything else")).json()
    assert second["relationshipDelta"]==0 and second["relationshipScore"]==490

def test_recent_completed_history_is_supplied_to_model() -> None:
    backend=FakeBackend(["POSITIVE","NEUTRAL"])
    client=TestClient(create_app(settings(),backend))
    client.post("/v2/conversation",json=payload("My dog's name is Bruno."))
    client.post("/v2/conversation",json=payload("Do you remember his name?"))
    assert "Bruno" in backend.users[1] and "A character-specific reply number 1." in backend.users[1]

def test_failed_model_call_does_not_change_score(tmp_path: Path) -> None:
    db=tmp_path/"memory.db"
    response=TestClient(create_app(settings(db),BrokenBackend())).post("/v2/conversation",json=payload()).json()
    assert not response["success"] and response["errorCode"]=="backend_error"
    store=MemoryStore(db)
    assert store.snapshot("stardew_valley","player","Linus").score==500
    assert store.connection.execute("SELECT status FROM interactions").fetchone()[0]=="FAILED"

def test_cancellation_prevents_late_commit() -> None:
    store=MemoryStore(Path(":memory:"))
    before=store.snapshot("game","player","npc")
    iid=store.begin("12345678","game","player","npc","hello",before)
    assert store.mark(iid,"CANCELLED")
    assert store.finish(iid,"late","POSITIVE","smile",{"POSITIVE":10,"NEUTRAL":0,"NEGATIVE":-10}) is None
    assert store.snapshot("game","player","npc").score==500

def test_stale_concurrent_result_is_superseded() -> None:
    store=MemoryStore(Path(":memory:"))
    before=store.snapshot("game","player","npc")
    first=store.begin("first-id","game","player","npc","one",before)
    second=store.begin("second-id","game","player","npc","two",before)
    deltas={"POSITIVE":10,"NEUTRAL":0,"NEGATIVE":-10}
    assert store.finish(first,"one","POSITIVE","smile",deltas)
    assert store.finish(second,"two","POSITIVE","smile",deltas) is None
    statuses=dict(store.connection.execute("SELECT interaction_id,status FROM interactions"))
    assert statuses["second-id"]=="SUPERSEDED"

@pytest.mark.parametrize("score,state",[(0,"HOSTILE"),(200,"VERY_NEGATIVE"),(300,"OFFENDED"),(400,"ANNOYED"),(450,"NEUTRAL"),(550,"FRIENDLY"),(650,"WARM"),(750,"TRUSTING"),(850,"VERY_CLOSE"),(1000,"VERY_CLOSE")])
def test_relationship_thresholds(score: int,state: str)->None:
    assert relationship_state(score)==state

def test_each_relationship_state_has_distinct_acting_direction() -> None:
    from npc_bridge.persona import RELATIONSHIP_ACTING
    assert set(RELATIONSHIP_ACTING)=={"VERY_CLOSE","TRUSTING","WARM","FRIENDLY","NEUTRAL","ANNOYED","OFFENDED","VERY_NEGATIVE","HOSTILE"}
    assert len(set(RELATIONSHIP_ACTING.values()))==9

def test_prompt_has_profile_state_and_no_keyword_classifier() -> None:
    request=ConversationRequestV2.model_validate(payload("You old fart."))
    profile=ProfileStore(settings().profiles_path).load("stardew_valley.linus")
    system,user=PersonaEngine.build_prompt(request,profile)
    assert "Linus" in system and "NEUTRAL (500/1000)" in system
    assert "You old fart." in user and "old fart" not in system

def test_malformed_output_retries_then_fails_without_score() -> None:
    backend=FakeBackend(malformed=True)
    response=TestClient(create_app(settings(),backend)).post("/v2/conversation",json=payload()).json()
    assert not response["success"] and response["errorCode"]=="backend_error" and backend.calls==2

def test_v1_remains_compatible() -> None:
    old={"protocolVersion":"1.0","game":"stardew_valley","npc":{"id":"Linus","displayName":"Linus","friendshipHearts":0},
         "world":{"location":"Mountain","season":"Spring","day":1,"time":740,"weather":"clear"},
         "player":{"name":"Player","message":"Hello."}}
    result=TestClient(create_app(settings(),FakeBackend())).post("/v1/conversation",json=old).json()
    assert result["protocolVersion"]=="1.0" and result["success"]

def test_legacy_database_is_migrated(tmp_path: Path) -> None:
    db=tmp_path/"legacy.db"
    connection=sqlite3.connect(db)
    connection.execute("""CREATE TABLE interactions(id INTEGER PRIMARY KEY,game_id TEXT,player_id TEXT,npc_id TEXT,
        category TEXT,relationship_delta INTEGER,message_excerpt TEXT,created_at TEXT)""")
    connection.execute("INSERT INTO interactions VALUES(1,'g','p','n','rude',-12,'bad','2026-01-01')")
    connection.commit(); connection.close()
    store=MemoryStore(db)
    assert store.snapshot("g","p","n").score==488
    assert store.connection.execute("SELECT status FROM interactions WHERE interaction_id='legacy-1'").fetchone()[0]=="COMPLETED"

def test_expression_has_no_body_language_field() -> None:
    result=TestClient(create_app(settings(),FakeBackend())).post("/v2/conversation",json=payload()).json()
    assert result["facialExpression"]=="a thoughtful frown" and "bodyLanguage" not in result

def test_body_movement_in_expression_is_retried() -> None:
    class ExpressionBackend(FakeBackend):
        async def generate(self,system,user,output_schema=None):
            self.calls+=1
            expression="nods slightly" if self.calls==1 else "a slight smile"
            return json.dumps({"dialogue":"Quiet weather.","sentiment":"NEUTRAL","facialExpression":expression})
    backend=ExpressionBackend()
    result=TestClient(create_app(settings(),backend)).post("/v2/conversation",json=payload()).json()
    assert result["success"] and result["facialExpression"]=="a slight smile" and backend.calls==2

def test_terse_or_repeated_dialogue_is_retried() -> None:
    class TerseBackend(FakeBackend):
        async def generate(self,system,user,output_schema=None):
            self.calls+=1
            dialogue="Don't." if self.calls==1 else "You have worn out your welcome here."
            return json.dumps({"dialogue":dialogue,"sentiment":"NEGATIVE","facialExpression":"an angry frown"})
    backend=TerseBackend()
    result=TestClient(create_app(settings(),backend)).post("/v2/conversation",json=payload("Leave me alone.")).json()
    assert result["success"] and result["dialogue"]=="You have worn out your welcome here." and backend.calls==2

def test_long_exact_recent_reply_is_retried() -> None:
    class RepeatingBackend(FakeBackend):
        async def generate(self,system,user,output_schema=None):
            self.calls+=1
            dialogue="That is enough. I do not appreciate that language around here." if self.calls<=2 else "Leave my camp until you can speak with respect."
            return json.dumps({"dialogue":dialogue,"sentiment":"NEGATIVE","facialExpression":"a stern frown"})
    backend=RepeatingBackend()
    client=TestClient(create_app(settings(),backend))
    assert client.post("/v2/conversation",json=payload("First insult.")).json()["success"]
    second=client.post("/v2/conversation",json=payload("Second insult.")).json()
    assert second["dialogue"]=="Leave my camp until you can speak with respect." and backend.calls==3
