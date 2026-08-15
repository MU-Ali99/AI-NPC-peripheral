$ErrorActionPreference = 'Stop'
$body = @{
    protocolVersion = '2.0'; game = @{ id = 'stardew_valley'; name = 'Stardew Valley' }
    npc = @{ id = 'Abigail'; displayName = 'Abigail'; profileId = 'stardew_valley.abigail' }
    world = @{ location = 'Town'; season = 'Fall'; day = 14; time = 2040; weather = 'rain' }
    player = @{ id = 'player'; displayName = 'Player'; message = 'Why do you like spending so much time outside?' }
    relationship = @{ level = 5; label = 'friendship_hearts' }
    context = @{ custom = @{} }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/v2/conversation' -ContentType 'application/json' -Body $body | ConvertTo-Json
