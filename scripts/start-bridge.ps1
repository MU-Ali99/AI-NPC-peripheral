$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Virtual environment not found. Run scripts\setup-dev.ps1 first.'
}
Set-Location (Join-Path $projectRoot 'npc-bridge')
& $python -m npc_bridge

