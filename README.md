# AI NPC Peripheral

This is a local prototype for talking to game characters through a language model. Stardew Valley is the first game adapter, but the bridge runs as a separate service so it can later move to another PC or a dedicated device.

```text
Stardew Valley -> SMAPI mod -> NPCBridge -> Ollama
```

The current build is text-only. Walk near a supported character, press `Alt+0`, type a message, and the reply is shown in a Stardew dialogue box.

## What works

- Stardew Valley 1.6.0 with SMAPI 4.0.6
- Configurable `Alt+0` conversation key
- Nearest-villager detection
- Custom in-game text input
- Non-blocking HTTP requests while the model generates a reply
- Player, relationship, location, date, time, and weather context
- Abigail and Linus character profiles
- Local inference through Ollama and `qwen3:4b-instruct-2507-q4_K_M`
- Python source mode and a packaged `NPCBridge.exe`
- Request validation, timeouts, readable errors, and automated tests
- Generic protocol v2 with protocol v1 compatibility
- Structured dialogue output with emotion metadata and safe fallback handling
- Persona regression checks for normal, technical, hostile, and adversarial messages
- Character-specific speech cadence, vocabulary, habits, and reaction patterns
- Persistent 0–1000 per-player relationship scores and complete recent dialogue history
- Model-owned POSITIVE/NEUTRAL/NEGATIVE judgments with deterministic score changes
- Transaction-safe pending, completed, cancelled, failed, and superseded interactions
- Visible facial expressions in the dialogue box
- Conversation outcomes applied to Stardew friendship points
- Paused single-player input and waiting screens

## Project layout

- `stardew-mod/StardewAI/` - the SMAPI game adapter
- `npc-bridge/` - the standalone dialogue service
- `npc-profiles/` - character profiles used by the bridge
- `protocol/` - the HTTP/JSON contract
- `config/` - bridge defaults
- `tests/` - bridge tests
- `scripts/` - setup, build, startup, and test scripts
- `docs/` - release notes and technical notes

Game files, model files, build output, and local configuration are intentionally excluded from Git.

## Requirements

The prototype was built and tested with:

- Windows 11
- Stardew Valley 1.6.0 (GOG)
- SMAPI 4.0.6
- .NET SDK 10, targeting .NET 6 for the mod
- Python 3.12
- Ollama 0.32.9
- `qwen3:4b-instruct-2507-q4_K_M`

SMAPI is pinned to 4.0.6 because newer releases require a newer Stardew Valley version.

## Running it

From PowerShell in the project folder:

```powershell
.\scripts\start-system.ps1
```

Then launch Stardew through:

```text
C:\Games\Stardew Valley\StardewModdingAPI.exe
```

Load a save, walk within four tiles of Abigail or Linus, and press `Alt+0` on the top number row. Enter submits the message and Escape cancels either typing or a request that is still generating.

Do not launch `Stardew Valley.exe` directly; that starts the game without SMAPI or the mod.

## Development setup

Create the virtual environment and install the Python dependencies:

```powershell
.\scripts\setup-dev.ps1
```

Run the bridge from source:

```powershell
.\scripts\start-bridge.ps1
```

Test a running bridge:

```powershell
.\scripts\test-bridge.ps1
```

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_bridge.py
```

Run the live persona regression suite against the configured model:

```powershell
.\scripts\persona-regression.ps1
```

Reports are saved under the ignored local `reports` directory.

## Building

Build and install the Stardew mod:

```powershell
.\scripts\build-mod.ps1
.\scripts\install-mod.ps1
```

Build the Windows bridge package:

```powershell
.\scripts\build-bridge-exe.ps1
```

The packaged service is written to `artifacts\NPCBridge`. Keep the executable, `config`, and `npc-profiles` together when moving it.

## Configuration

Bridge defaults live in `config/default.json`. They can be overridden with these environment variables:

- `NPCBRIDGE_HOST`
- `NPCBRIDGE_PORT`
- `NPCBRIDGE_OLLAMA_ENDPOINT`
- `NPCBRIDGE_MODEL`
- `NPCBRIDGE_CONFIG`
- `NPCBRIDGE_PROFILES`
- `NPCBRIDGE_MEMORY`

The mod writes its local settings to `C:\Games\Stardew Valley\Mods\StardewAI\config.json`. That file controls the hotkey, bridge address, timeout, and interaction distance.

NPCBridge binds to `127.0.0.1` by default. A future game adapter can point to a LAN address without embedding the model inside the game mod.

## Troubleshooting

- If the hotkey does nothing, make sure the game was launched through `StardewModdingAPI.exe`.
- If the bridge is unavailable, run `scripts\start-system.ps1` and then `scripts\test-bridge.ps1`.
- If a character has no profile, the bridge returns a safe error. Only Abigail and Linus are included right now.
- The first response can be slower because Ollama needs to load the model into memory.
- SMAPI logs are stored under `%APPDATA%\StardewValley\ErrorLogs`.
- Leave SMAPI at 4.0.6 while using Stardew Valley 1.6.0.

## Current limits

- Text conversation only
- Two character profiles
- Relationship behavior is intentionally limited to three sentiment outcomes in this milestone
- No voice input or speech output
- No generated quests or character movement
- No API authentication while running on localhost

The first working snapshot is tagged `v0.1.0`. Version `v0.4.0` moves language judgment into the model and makes NPCBridge the transactional owner of scores and conversation history. Version `v0.4.1` changes the model and makes relationship stages explicit acting directions. Earlier release details are kept in `docs/releases`.
