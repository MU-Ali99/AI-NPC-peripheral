using System.Text.Json.Serialization;

namespace StardewAI;

internal sealed record ConversationRequest(
    [property: JsonPropertyName("protocolVersion")] string ProtocolVersion,
    [property: JsonPropertyName("game")] string Game,
    [property: JsonPropertyName("npc")] NpcContext Npc,
    [property: JsonPropertyName("world")] WorldContext World,
    [property: JsonPropertyName("player")] PlayerContext Player
);

internal sealed record NpcContext(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("displayName")] string DisplayName,
    [property: JsonPropertyName("friendshipHearts")] int FriendshipHearts
);

internal sealed record WorldContext(
    [property: JsonPropertyName("location")] string Location,
    [property: JsonPropertyName("season")] string Season,
    [property: JsonPropertyName("day")] int Day,
    [property: JsonPropertyName("time")] int Time,
    [property: JsonPropertyName("weather")] string Weather
);

internal sealed record PlayerContext(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("message")] string Message
);

internal sealed record ConversationResponse(
    [property: JsonPropertyName("protocolVersion")] string ProtocolVersion,
    [property: JsonPropertyName("success")] bool Success,
    [property: JsonPropertyName("npc")] string Npc,
    [property: JsonPropertyName("dialogue")] string Dialogue,
    [property: JsonPropertyName("error")] string? Error
);

internal sealed record PendingDialogue(string NpcId, string? Dialogue, string? Error);

