# Development Notes

Last updated: August 16, 2026

## What we are building

The first goal was simple: type a message to a Stardew character and get a local AI reply back inside the game.

```text
player message
  -> Stardew mod
  -> NPCBridge
  -> Ollama
  -> NPCBridge
  -> Stardew dialogue box
```

That loop now works. We are keeping this version as the reference demo instead of continuing to change it while it is stable.

## Why the pieces are separate

The Stardew mod reads game information and handles the game UI. NPCBridge handles character profiles, memory, relationship scores, prompts, model calls, and response checks.

Keeping those jobs separate makes the project easier to debug. It also means a future game only needs a new adapter instead of a complete rewrite.

## Current local setup

- Stardew Valley 1.6.0
- SMAPI 4.0.6
- .NET SDK 10 with a .NET 6 mod target
- Python 3.12
- Ollama 0.32.9
- `qwen3:4b-instruct-2507-q4_K_M`

The repository does not store or assume a local game installation location. Build and install scripts read it from `STARDEW_GAME_PATH`, and the installer also accepts `-GamePath`.

SMAPI 4.0.6 is intentional. The game is staying on version 1.6.0, and newer SMAPI releases expect a newer game version.

## Main decisions

- The game mod is the only part that reads Stardew state.
- The bridge runs as a separate local HTTP service.
- Ollama access sits behind an `LlmBackend` interface.
- Character profiles live outside the game mod and model backend.
- Model requests do not block Stardew's main thread.
- Replies return to the game thread before touching the UI.
- AI conversations use their own hotkey and do not replace normal dialogue.
- The model judges a message as positive, neutral, or negative.
- NPCBridge turns that result into a configured score change.
- SQLite owns saved interactions and relationship state.
- Interaction IDs stop cancelled, repeated, or old replies from changing state.
- NPCBridge listens on localhost unless someone changes the configuration.

## What we verified

- 25 Python tests pass.
- Source-mode health and conversation requests work.
- The packaged `NPCBridge.exe` works.
- Abigail and Linus both return local model dialogue.
- The Stardew mod builds in Release mode.
- SMAPI loads the mod on Stardew Valley 1.6.0.
- The conversation key is `Alt+0`.
- Enter sends a message and Escape cancels cleanly.
- Protocol v1 and v2 both work.
- Protocol v2 carries interaction IDs, sentiment, score, and relationship state.
- In-game tests showed mixed praise and insults, recent recall, guarded apologies, persistent tone, and expression text.

The old SMAPI and game assemblies produce a Newtonsoft version warning during the mod build. The mod does not use Newtonsoft directly, and the built assembly loads correctly.

## Finished milestones

- Installed and checked SMAPI 4.0.6
- Set up Python and Ollama
- Tested local models and selected Qwen 3 4B Instruct
- Built the standalone bridge
- Added versioned conversation endpoints
- Added Abigail and Linus profiles
- Built the Stardew adapter and custom text box
- Added nearby-character detection
- Connected Stardew to the bridge without freezing the game thread
- Packaged NPCBridge as a Windows executable
- Added structured responses and character regression checks
- Added persistent memory, relationship scores, and grudges
- Added facial-expression text and Stardew friendship effects
- Added request cancellation and stale-reply protection
- Recorded a full player-controlled in-game test

## How this version developed

The first working build proved the full local conversation loop. Later passes separated the protocol from Stardew, improved individual character voices, added memory and relationship effects, fixed text-input problems, and made hostile replies less generic.

Version 0.4.0 moved language judgment into the model while leaving score storage and transaction safety in NPCBridge. Version 0.4.1 switched to Qwen 3 4B Instruct because it handled character voice, recall, and confrontation better on this machine. Version 0.4.2 reduced prompt size, capped output, and preloaded the model to improve response time.

Full details are available in `docs/releases`.

## Current rough edges

- A cold model request can take roughly 35–55 seconds on CPU.
- Warm replies have usually taken around 7–10 seconds in local tests.
- Hostile relationship stages feel more distinct than positive stages.
- Apologies at very negative scores can sound too repetitive and unforgiving.
- Three sentiment labels are useful for this demo but too simple for a deeper relationship system.
- Only two character profiles exist.

## When work resumes

Start from a fresh Git checkpoint and compare changes against `docs/WORKING_PROTOTYPE.md`. The first useful improvement is gradual reconciliation, followed by clearer positive relationship stages.

Change one behavior at a time. The current prototype is already a good proof that the bridge, local model, memory, and game adapter can work together.
