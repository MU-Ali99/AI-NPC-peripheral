$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$ollama = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
$bridge = Join-Path $projectRoot 'artifacts\NPCBridge\NPCBridge.exe'
if (-not (Test-Path -LiteralPath $ollama)) { throw 'Ollama is not installed.' }
if (-not (Test-Path -LiteralPath $bridge)) { throw 'NPCBridge.exe is missing. Run scripts\build-bridge-exe.ps1.' }
try {
    Invoke-RestMethod 'http://127.0.0.1:11434/api/version' -TimeoutSec 2 | Out-Null
} catch {
    Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
}
try {
    Invoke-RestMethod 'http://127.0.0.1:8765/health' -TimeoutSec 2 | Out-Null
    Write-Output 'NPCBridge is already running at http://127.0.0.1:8765.'
} catch {
    Start-Process -FilePath $bridge -WorkingDirectory (Split-Path -Parent $bridge)
    Write-Output 'NPCBridge started. Leave its window open while playing.'
}

