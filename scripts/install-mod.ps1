$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'stardew-mod\StardewAI\bin\Release\net6.0'
$target = 'C:\Games\Stardew Valley\Mods\StardewAI'
if (-not (Test-Path -LiteralPath (Join-Path $source 'StardewAI.dll'))) { throw 'Build output is missing. Run scripts\build-mod.ps1 first.' }
New-Item -ItemType Directory -Path $target -Force | Out-Null
@('StardewAI.dll', 'StardewAI.pdb') | ForEach-Object {
    Copy-Item -LiteralPath (Join-Path $source $_) -Destination (Join-Path $target $_) -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'stardew-mod\StardewAI\manifest.json') -Destination (Join-Path $target 'manifest.json') -Force
Write-Output "Installed StardewAI to $target"
