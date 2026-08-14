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
- SMAPI status: not installed (`StardewModdingAPI.exe`, `Mods`, and `smapi-internal` absent).
- No original game files were modified during inspection.
- Current SMAPI 4.5.2 requires Stardew Valley 1.6.14 or later, so the game must be updated before installing current SMAPI.
- Vanilla launch and SMAPI launch verification remain pending.

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

1. Inspect Stardew and prepare SMAPI development — **blocked pending game update to 1.6.14+**, then SMAPI install and launch verification.
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

1. Update the GOG Stardew Valley installation to version 1.6.14 or later.
2. Launch vanilla Stardew once and close it.
3. Install the current official SMAPI release using its standard installer.
4. Verify launch through SMAPI.
5. Install Python and Ollama, then continue bridge implementation.

