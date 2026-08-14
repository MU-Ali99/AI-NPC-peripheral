$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$project = Join-Path $projectRoot 'stardew-mod\StardewAI\StardewAI.csproj'
dotnet build $project --configuration Release

