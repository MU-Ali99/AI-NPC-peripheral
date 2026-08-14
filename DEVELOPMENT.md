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
- SMAPI file/version verification passed. Interactive game launch verification remains pending.

### Development tools

- Git: `2.54.0.windows.1` installed.
- .NET SDK: `10.0.203` installed; target framework requirements will be selected when scaffolding the SMAPI project.
- Python: not installed. The `python.exe` command currently resolves only to the nonfunctional Microsoft Store alias.
- Python launcher (`py`): not installed.
- Ollama: not installed.

## Safety and repository policy

- The local `Stardew Valley/` installer folder in this workspace is excluded from Git and will remain untouched.
- The installed game at `C:\Games\Stardew Valley` is external to this repository.
- Game binaries/assets, SMAPI redistributables, model files, secrets, build outputs, and machine-local configuration must not be committed.

## Milestone status

1. Inspect Stardew and prepare SMAPI development — **in progress**; inspection and SMAPI 4.0.6 installation complete, interactive launch verification pending.
2. Check/install dependencies — **in progress**; Git and .NET found, Python and Ollama missing.
3. Configure Ollama and verify inference — pending.
4. Build NPCBridge — pending.
5. Test NPCBridge over HTTP — pending.
6. Create and load basic SMAPI mod — pending.
7. Implement Alt+1 NPC detection — pending.
8. Implement in-game text input — pending.
9. Connect SMAPI to NPCBridge — pending.
10. Connect NPCBridge to Ollama — pending.
11. Return dialogue to Stardew — pending.
12. Complete Abigail end-to-end test — pending.
13. Package NPCBridge as a Windows executable — pending.

## Next actions

1. Launch `C:\Games\Stardew Valley\StardewModdingAPI.exe`, reach the title screen, then close it to verify SMAPI startup.
2. Install Python and Ollama, then continue bridge implementation.
