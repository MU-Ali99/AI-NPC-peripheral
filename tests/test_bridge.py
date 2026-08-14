from pathlib import Path

from fastapi.testclient import TestClient

from npc_bridge.app import clean_dialogue, create_app
from npc_bridge.backends import LlmBackend, LlmBackendError
from npc_bridge.config import Settings


class FakeBackend(LlmBackend):
    async def generate(self, system: str, user: str) -> str:
        assert "Abigail" in system
        assert "Why are you outside?" in user
        return 'Abigail: "The rain makes everything feel like an adventure."'


class BrokenBackend(LlmBackend):
    async def generate(self, system: str, user: str) -> str:
        raise LlmBackendError("model offline")


def settings() -> Settings:
    return Settings(profiles_path=Path(__file__).parents[1] / "npc-profiles")


def request() -> dict:
    return {
        "protocolVersion": "1.0",
        "game": "stardew_valley",
        "npc": {"id": "Abigail", "displayName": "Abigail", "friendshipHearts": 5},
        "world": {"location": "Town", "season": "Fall", "day": 14, "time": 2040, "weather": "rain"},
        "player": {"name": "Player", "message": "Why are you outside?"},
    }


def test_conversation_success() -> None:
    response = TestClient(create_app(settings(), FakeBackend())).post("/v1/conversation", json=request())
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["dialogue"] == "The rain makes everything feel like an adventure."


def test_backend_failure_is_safe() -> None:
    response = TestClient(create_app(settings(), BrokenBackend())).post("/v1/conversation", json=request())
    assert response.status_code == 200
    assert response.json() == {"protocolVersion": "1.0", "success": False, "npc": "Abigail", "dialogue": "", "error": "model offline"}


def test_unknown_profile_is_safe() -> None:
    payload = request()
    payload["npc"]["id"] = "Unknown"
    response = TestClient(create_app(settings(), FakeBackend())).post("/v1/conversation", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_validation_rejects_empty_message() -> None:
    payload = request()
    payload["player"]["message"] = ""
    assert TestClient(create_app(settings(), FakeBackend())).post("/v1/conversation", json=payload).status_code == 422


def test_clean_dialogue_truncates_on_word_boundary() -> None:
    result = clean_dialogue("one two three four", 14)
    assert result == "one two…"

