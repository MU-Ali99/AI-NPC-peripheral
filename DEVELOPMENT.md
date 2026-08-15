# Development Log

Last updated: 2026-08-13

## Architecture decisions

- Keep the SMAPI game adapter and NPCBridge in separate processes.
- Communicate using a versioned HTTP/JSON protocol.
- Keep prompt construction, profiles, and LLM integration in NPCBridge.
- Model the LLM behind a replaceable backend interface; Ollama is only the first implementation.
- Keep machine-specific paths in ignored local configuration or documentation, never scattered through source.
- Preserve normal Stardew interactions; AI dialogue will use a separate configurable hotkey.

## Environment discovery

### Stardew Valley

- Installation path: `C:\Games\Stardew Valley`
- Distribution indicators: GOG metadata is present.
- Executable: `C:\Games\Stardew Valley\Stardew Valley.exe`
- Detected file/product version: `1.6.0.24079` / `1.6.0`
- SMAPI status: version `4.0.6` manually installed from the official GitHub release payload using the release's documented manual procedure.
- SMAPI executable: `C:\Games\Stardew Valley\StardewModdingAPI.exe`
- Bundled mods installed: Console Commands and Save Backup.
- SMAPI installer archive SHA-256: `8BD7373F10E05BAD969483CC963E785E49B9511A42D9ABF7E82E49E8518CDB8E`.
- No original game files were modified during inspection.
- The project intentionally pins SMAPI 4.0.6 because the game will remain on Stardew Valley 1.6.0. SMAPI 4.0.6 is the last release explicitly documented for Stardew Valley 1.6.0 or later; newer SMAPI releases require newer game versions.
- SMAPI file/version and title-screen launch verification passed.

### Development tools

- Git: `2.54.0.windows.1` installed.
- .NET SDK: `10.0.203` installed; the mod targets .NET 6 for the pinned game/SMAPI build.
- Python: `3.12.10` installed through winget (`Python.Python.3.12`).
- Ollama: `0.32.9` installed through winget (`Ollama.Ollama`); API verified at `http://127.0.0.1:11434`.
- Model: `qwen2.5:1.5b`, approximately 986 MB model payload, pulled with `ollama pull qwen2.5:1.5b`.

## Safety and repository policy

- The local `Stardew Valley/` installer folder in this workspace is excluded from Git and will remain untouched.
- The installed game at `C:\Games\Stardew Valley` is external to this repository.
- Game binaries/assets, SMAPI redistributables, model files, secrets, build outputs, and machine-local configuration must not be committed.

## Milestone status

1. Inspect Stardew and prepare SMAPI development — **complete**; SMAPI launched the game and loaded the mod at the title screen.
2. Check/install dependencies — **complete**.
3. Configure Ollama and verify inference — **complete**.
4. Build NPCBridge — **complete**.
5. Test NPCBridge over HTTP — **complete**; five automated tests plus live Ollama calls pass.
6. Create and load basic SMAPI mod — **complete**; confirmed in SMAPI log.
7. Implement Alt+0 NPC detection — **complete**.
8. Implement in-game text input — **complete**.
9. Connect SMAPI to NPCBridge — **complete**.
10. Connect NPCBridge to Ollama — **complete**.
11. Return dialogue to Stardew — **implemented; interactive verification pending**.
12. Complete Abigail end-to-end test — **interactive in-save acceptance test pending**.
13. Package NPCBridge as a Windows executable — **complete and live-tested**.

## Next actions

1. Run `scripts\start-system.ps1`.
2. Launch SMAPI, load a save, stand beside Abigail or Linus, and complete the documented Alt+0 acceptance test.

## Verification record

- Python tests: 5 passed.
- Live source bridge health and conversation calls: passed.
- Live packaged EXE health and conversation calls: passed.
- C# Release build: passed with zero errors. A Newtonsoft version-resolution warning originates from the pinned legacy build package/game assembly combination and the mod does not directly use Newtonsoft.
- Initial SMAPI startup verification passed on 2026-08-13 with Stardew AI 0.1.0 and `LeftAlt + D1`. Version 0.1.1 changes the configured input to `LeftAlt + D0` (`Alt+0`).
- Full in-save UI interaction cannot be automated safely and remains the only acceptance test.
- Linus was added as the second original external profile to make the first interaction test easier near his mountain tent.
