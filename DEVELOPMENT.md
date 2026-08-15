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
- Model: `qwen2.5:1.5b`

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

## What has been verified

- Six Python tests pass.
- Source-mode bridge health and conversation requests pass.
- Packaged `NPCBridge.exe` health and conversation requests pass.
- Live requests through Ollama return dialogue for Abigail and Linus.
- The Stardew mod builds in Release mode with no compile errors.
- SMAPI 4.0.6 launches Stardew 1.6.0 and loads Stardew AI successfully.
- The mod configuration now uses `LeftAlt + D0`, shown to players as `Alt+0`.

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
- [ ] Complete and record a full player-controlled conversation in a loaded save

## Releases

### v0.1.0

First working local prototype. It includes the bridge, Ollama backend, Stardew adapter, Abigail and Linus profiles, packaging scripts, and automated tests. The original conversation key was `Alt+1`.

### v0.1.1

Changed the in-game conversation key to `Alt+0` and updated the installed mod configuration.

Detailed notes for the first snapshot are in `docs/releases/v0.1.0.md`.

## Next work

The next refactor should keep the current network and mod path working while making the bridge protocol fully game-agnostic. The main tasks are:

1. Introduce a generic conversation envelope without silently breaking protocol version 1.
2. Load profiles by an explicit `profileId`.
3. Separate persona rules from general knowledge instructions.
4. Validate structured model output and keep optional emotion metadata.
5. Add persona regression prompts for normal, technical, hostile, and adversarial messages.
6. Keep the Stardew menu open in a waiting state so single-player remains paused until the reply is shown.

The current implementation should be treated as the baseline, not replaced wholesale.
