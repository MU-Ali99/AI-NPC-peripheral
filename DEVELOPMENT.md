# Development Notes

Last updated: 2026-08-15

## Goal

The first milestone is a complete local text conversation:

```text
player message
  -> Stardew SMAPI adapter
  -> NPCBridge HTTP API
  -> Ollama
  -> NPCBridge
  -> Stardew dialogue box
```

The game adapter and dialogue service are separate on purpose. The mod gathers game state, while NPCBridge owns profiles, prompt construction, model access, validation, and response cleanup. Moving the bridge to another machine should only require changing its address in the mod configuration.

## Local environment

- Stardew Valley: `1.6.0`, build `24079`, GOG installation
- Game folder: `C:\Games\Stardew Valley`
- SMAPI: `4.0.6`
- Git: `2.54.0`
- .NET SDK: `10.0.203`
- Python: `3.12.10`
- Ollama: `0.32.9`
- Model: `qwen2.5:3b` (selected after persona regression testing on this 8 GB system)

SMAPI 4.0.6 is intentionally pinned because the game is staying on 1.6.0. The official SMAPI installer payload was downloaded from its GitHub release. Its SHA-256 was:

```text
8BD7373F10E05BAD969483CC963E785E49B9511A42D9ABF7E82E49E8518CDB8E
```

The game executable and original assets were not replaced. The repository ignores the local installer folder, game files, models, build output, secrets, and machine-specific configuration.

## Design choices

- SMAPI is the only component that reads Stardew state.
- NPCBridge runs independently and communicates over HTTP/JSON.
- Model access sits behind an `LlmBackend` interface.
- Profiles live outside both the mod and model backend.
- Network work runs asynchronously so Stardew's main thread stays responsive.
- Results are queued back to the game thread before touching Stardew UI state.
- Normal Stardew conversations are left alone; generated dialogue uses a separate key.
- The bridge binds to localhost unless configured otherwise.
- Relationship judgments use bounded deterministic rules after the model classifies the interaction. This keeps friendship changes predictable.
- Compact interaction memory is stored in SQLite and scoped by game, player, and NPC.

## What has been verified

- Twenty-one Python tests pass.
- Source-mode bridge health and conversation requests pass.
- Packaged `NPCBridge.exe` health and conversation requests pass.
- Live requests through Ollama return dialogue for Abigail and Linus.
- The Stardew mod builds in Release mode with no compile errors.
- SMAPI 4.0.6 launches Stardew 1.6.0 and loads Stardew AI successfully.
- The mod configuration now uses `LeftAlt + D0`, shown to players as `Alt+0`.
- Packaged NPCBridge reports protocols 1.0 and 2.0 and completes real v2 requests through `qwen2.5:3b`.
- Stardew AI uses the v2 endpoint at `http://127.0.0.1:8765/v2/conversation`.

The mod build reports a Newtonsoft version-resolution warning caused by the older SMAPI/game assembly combination. The mod does not use Newtonsoft directly, and the resulting assembly loads successfully.

## Milestones

- [x] Inspect the game installation
- [x] Install and verify SMAPI 4.0.6
- [x] Install Python and Ollama
- [x] Pull and test a small local model
- [x] Build NPCBridge
- [x] Add a versioned conversation endpoint
- [x] Add external profiles for Abigail and Linus
- [x] Build the SMAPI adapter
- [x] Add nearest-villager detection
- [x] Add the in-game text field
- [x] Connect the mod to the bridge asynchronously
- [x] Return generated dialogue to Stardew
- [x] Package NPCBridge as a Windows executable
- [x] Verify the mod loads through SMAPI
- [x] Add a game-neutral v2 adapter contract while retaining v1
- [x] Add structured output validation and persona regression tooling
- [x] Keep single-player paused during text input and model generation
- [x] Persist per-character interaction memory and grudges
- [x] Apply bounded conversation effects to Stardew friendship
- [x] Show a facial expression with each response
- [ ] Complete and record a full player-controlled conversation in a loaded save

## Releases

### v0.1.0

First working local prototype. It includes the bridge, Ollama backend, Stardew adapter, Abigail and Linus profiles, packaging scripts, and automated tests. The original conversation key was `Alt+1`.

### v0.1.1

Changed the in-game conversation key to `Alt+0` and updated the installed mod configuration.

### v0.2.0

Introduced the game-agnostic v2 envelope, explicit profile IDs, optional context fields, a dedicated PersonaEngine, structured-output validation with a compatible JSON fallback, injection checks, persona regression tooling, and a paused Stardew waiting menu. Protocol v1 remains available for older adapters.

### v0.2.1

Expanded profiles with unique speech cadence, vocabulary, verbal habits, phrases to avoid, and situation-specific reactions. Added interaction classification for insults and prompt-injection attempts, plus guards against generic assistant and counselor phrasing.

### v0.3.0

Added persistent per-player relationship memory. Compliments now have diminishing returns, repeated flattery can become uncomfortable, and insults or hostility can create wariness and grudges. Replies include facial expression and body language, while the Stardew adapter applies the returned impact to the NPC's real friendship score.

### v0.3.1

Removed body-language narration from the dialogue box, made facial expressions specific instead of showing neutral defaults, strengthened character reactions to direct insults, and raised the reply limit so detailed answers are possible when appropriate.

### v0.3.2

Added a stricter quality gate for insult responses. Linus no longer accepts self-pitying or wounded dialogue that conflicts with his calm, self-reliant profile.

### v0.3.3

Stopped text-entry keystrokes from reaching Stardew's normal menu shortcuts, including `E`. Added Escape cancellation while the model is generating, stale-response cleanup, clearer bridge errors, and expression text that works with both phrases and descriptions.

Detailed notes for the first snapshot are in `docs/releases/v0.1.0.md`.

## Next work

The next useful pass is richer long-term memory: gradual grudge recovery, character-specific sensitivity values, and a small in-game indication of the friendship change. The current implementation should remain the working baseline.
