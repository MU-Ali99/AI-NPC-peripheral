$ErrorActionPreference = 'Stop'
$body = @{
    protocolVersion = '1.0'; game = 'stardew_valley'
    npc = @{ id = 'Abigail'; displayName = 'Abigail'; friendshipHearts = 5 }
    world = @{ location = 'Town'; season = 'Fall'; day = 14; time = 2040; weather = 'rain' }
    player = @{ name = 'Player'; message = 'Why do you like spending so much time outside?' }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/v1/conversation' -ContentType 'application/json' -Body $body | ConvertTo-Json

