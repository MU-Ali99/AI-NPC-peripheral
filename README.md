# AI NPC Peripheral

Local-first prototype connecting Stardew Valley to a standalone AI dialogue service over HTTP/JSON.

```text
Stardew Valley -> SMAPI mod -> NPCBridge -> replaceable LLM backend (initially Ollama)
```

The first milestone is a text-only conversation with Abigail using a configurable `Alt+1` hotkey. Voice, autonomous movement, generated quests, and complex memory are intentionally out of scope.

## Status

Project initialization and environment discovery are in progress. See [DEVELOPMENT.md](DEVELOPMENT.md) for findings and milestone status.

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

