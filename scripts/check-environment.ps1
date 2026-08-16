param([string]$GamePath = $env:STARDEW_GAME_PATH)

$checks = @(
    @{ Name = 'Python 3.12'; Path = (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe') },
    @{ Name = 'Ollama'; Path = (Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe') }
)
if (-not [string]::IsNullOrWhiteSpace($GamePath)) {
    $checks = @(
        @{ Name = 'Stardew Valley'; Path = (Join-Path $GamePath 'Stardew Valley.exe') },
        @{ Name = 'SMAPI'; Path = (Join-Path $GamePath 'StardewModdingAPI.exe') }
    ) + $checks
} else {
    Write-Warning 'Set STARDEW_GAME_PATH or pass -GamePath to check Stardew Valley and SMAPI.'
}
$checks | ForEach-Object { [PSCustomObject]@{ Component = $_.Name; Found = Test-Path -LiteralPath $_.Path; Path = $_.Path } } | Format-Table -AutoSize
try { Invoke-RestMethod 'http://127.0.0.1:11434/api/version' -TimeoutSec 3 | Format-List } catch { Write-Warning 'Ollama API unavailable.' }
