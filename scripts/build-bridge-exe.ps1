$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$output = Join-Path $projectRoot 'artifacts\NPCBridge'
New-Item -ItemType Directory -Path $output -Force | Out-Null
& $python -m PyInstaller --noconfirm --clean --onefile --name NPCBridge --paths (Join-Path $projectRoot 'npc-bridge\src') --distpath $output --workpath (Join-Path $projectRoot 'build\pyinstaller') --specpath (Join-Path $projectRoot 'build') (Join-Path $projectRoot 'npc-bridge\launcher.py')
Copy-Item -LiteralPath (Join-Path $projectRoot 'config') -Destination $output -Recurse -Force
Copy-Item -LiteralPath (Join-Path $projectRoot 'npc-profiles') -Destination $output -Recurse -Force
Write-Output "Built $(Join-Path $output 'NPCBridge.exe')"
