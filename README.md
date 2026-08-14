# AI NPC Peripheral

Local-first prototype connecting Stardew Valley to a standalone AI dialogue service over HTTP/JSON.

```text
Stardew Valley -> SMAPI mod -> NPCBridge -> replaceable LLM backend (initially Ollama)
```

The first milestone is a text-only conversation with Abigail using a configurable `Alt+1` hotkey. Voice, autonomous movement, generated quests, and complex memory are intentionally out of scope.

## Current prototype

The complete MVP is implemented and installed locally:

- Stardew Valley `1.6.0` with pinned SMAPI `4.0.6`.
- Stardew AI SMAPI mod with configurable `Alt+1` activation.
- In-game text entry, nearest-NPC targeting, world/relationship context, and non-blocking HTTP.
- NPCBridge FastAPI service with a versioned protocol and replaceable LLM backend.
- Ollama `0.32.9` with `qwen2.5:1.5b` (approximately 986 MB model payload).
- External original Abigail profile.
- Standalone Windows `NPCBridge.exe` package.

Automated API, model, build, packaging, and SMAPI load checks pass. The remaining acceptance check is using `Alt+1` beside Abigail in a loaded save.

## Layout

- `stardew-mod/StardewAI/` — game adapter implemented as a SMAPI C# mod.
- `npc-bridge/` — standalone, game-agnostic AI middleware.
- `npc-profiles/` — original behavioral profiles, kept outside the mod.
- `protocol/` — versioned HTTP/JSON contract.
- `config/` — safe default configuration; local settings are ignored by Git.
- `tests/` — automated tests.
- `docs/` — architecture and operational documentation.
- `scripts/` — environment, startup, test, and packaging scripts.

Setup and usage instructions will be expanded as each component becomes operational.

## Quick start

1. Start the AI service:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\start-system.ps1
   ```

2. Launch the game through:

   ```text
   C:\Games\Stardew Valley\StardewModdingAPI.exe
   ```

3. Load a save, stand within four tiles of Abigail, and press `Alt+1`.
4. Type a message and press Enter. Press Escape to cancel.

The service must remain running while playing. Ollama normally starts with Windows; `start-system.ps1` also attempts to start it if needed.

## Development setup

Installed prerequisites:

- Git 2.54
- .NET SDK 10 (the mod targets .NET 6 to match this game build)
- Python 3.12.10
- Ollama 0.32.9
- Stardew Valley 1.6.0 and SMAPI 4.0.6

Create/update the Python environment:

```powershell
.\scripts\setup-dev.ps1
```

Start the Python source service:

```powershell
.\scripts\start-bridge.ps1
```

Test the running API:

```powershell
.\scripts\test-bridge.ps1
```

Run automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_bridge.py
```

## Build and install

Build and install the SMAPI mod:

```powershell
.\scripts\build-mod.ps1
.\scripts\install-mod.ps1
```

Build the standalone service:

```powershell
.\scripts\build-bridge-exe.ps1
```

Output is written to `artifacts\NPCBridge\`. Keep `NPCBridge.exe`, `config`, and `npc-profiles` together if moving the package.

## Configuration

NPCBridge defaults are in `config/default.json`. Environment overrides include `NPCBRIDGE_HOST`, `NPCBRIDGE_PORT`, `NPCBRIDGE_OLLAMA_ENDPOINT`, `NPCBRIDGE_MODEL`, `NPCBRIDGE_CONFIG`, and `NPCBRIDGE_PROFILES`.

The mod creates `C:\Games\Stardew Valley\Mods\StardewAI\config.json` on first launch. It controls the hotkey, bridge URL, timeout, and interaction distance. Keep the default loopback binding for local use. A future peripheral can use a LAN address without changing the mod code.

## Troubleshooting

- **Service unavailable:** run `scripts\start-system.ps1`, then open `http://127.0.0.1:8765/health` or run `scripts\test-bridge.ps1`.
- **Hotkey does nothing:** launch through `StardewModdingAPI.exe`, load a save, close other menus, and stand near a villager.
- **No profile:** the MVP intentionally supports Abigail only. Other NPCs return a safe error until a profile is added.
- **Slow first response:** Ollama must load the model into memory on the first request.
- **SMAPI update notice:** do not update SMAPI beyond 4.0.6 while the game remains at 1.6.0.
- **Logs:** SMAPI logs are under `%APPDATA%\StardewValley\ErrorLogs`; NPCBridge logs to its console.

## Known limitations

- One NPC profile (Abigail), text-to-text only.
- No conversation memory, voice, generated quests, or autonomous behavior.
- Generated dialogue uses a compatible vanilla dialogue box on Stardew 1.6.0.
- The API has no authentication because it binds to `127.0.0.1` by default. Add network security before exposing it beyond the local PC.
