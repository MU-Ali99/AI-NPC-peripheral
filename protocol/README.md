# NPCBridge Adapter Contract

NPCBridge accepts standardized conversation envelopes from game adapters. It does not know how an adapter reads its game and never reads game memory, files, or engine objects itself.

```text
Game -> adapter -> HTTP/JSON -> NPCBridge -> LLM backend
```

## Current endpoints

- `POST /v2/conversation` - generic adapter protocol
- `POST /v1/conversation` - legacy Stardew protocol retained for compatibility
- `POST /conversation` - alias for v1
- `GET /health` - service, backend, and supported protocol information

## Adapter responsibilities

Every adapter provides a game ID, target NPC identity, explicit profile ID, player identity/message, and any relationship or world state the game supports. Unsupported concepts are omitted. `context.custom` carries small game-specific values without adding them to the core contract.

Adapters receive dialogue, visible-reaction text, and bounded relationship-impact metadata. An adapter may ignore fields its game cannot use. The Stardew adapter applies `relationshipDelta` directly as friendship points.

## Example v2 request

```json
{
  "protocolVersion": "2.0",
  "game": { "id": "stardew_valley", "name": "Stardew Valley" },
  "npc": { "id": "Linus", "displayName": "Linus", "profileId": "stardew_valley.linus" },
  "player": { "id": "1234", "displayName": "Player", "message": "Why do you live here?" },
  "relationship": { "level": 2, "label": "friendship_hearts" },
  "world": { "location": "Mountain", "time": "09:20", "day": 4, "season": "Spring", "weather": "Clear" },
  "context": { "nearbyCharacters": [], "recentEvents": [], "questState": {}, "custom": {} }
}
```

## Example response

```json
{
  "protocolVersion": "2.0",
  "success": true,
  "npc": "Linus",
  "dialogue": "The quiet here gives me room to notice the world changing around me.",
  "emotion": "neutral",
  "confidence": 0.86,
  "facialExpression": "a guarded half-smile",
  "bodyLanguage": "loosens his shoulders and studies the player",
  "relationshipDelta": 2,
  "relationshipReason": "A friendly exchange slightly improves the relationship.",
  "memoryState": "normal",
  "errorCode": null,
  "error": null
}
```

Handled failures use stable codes such as `profile_not_found`, `invalid_profile`, and `backend_error`. Invalid envelopes receive HTTP 422.

The JSON schemas in this directory are the portable contract. Protocol v1 remains frozen; incompatible changes belong in a new version.
