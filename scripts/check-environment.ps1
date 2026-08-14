$gameRoot = 'C:\Games\Stardew Valley'
$checks = @(
    @{ Name = 'Stardew Valley 1.6.0'; Path = (Join-Path $gameRoot 'Stardew Valley.exe') },
    @{ Name = 'SMAPI 4.0.6'; Path = (Join-Path $gameRoot 'StardewModdingAPI.exe') },
    @{ Name = 'Python 3.12'; Path = (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe') },
    @{ Name = 'Ollama'; Path = (Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe') }
)
$checks | ForEach-Object { [PSCustomObject]@{ Component = $_.Name; Found = Test-Path -LiteralPath $_.Path; Path = $_.Path } } | Format-Table -AutoSize
try { Invoke-RestMethod 'http://127.0.0.1:11434/api/version' -TimeoutSec 3 | Format-List } catch { Write-Warning 'Ollama API unavailable.' }

