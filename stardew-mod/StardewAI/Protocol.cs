using System.Text.Json.Serialization;

namespace StardewAI;

internal sealed record ConversationRequest(
    [property: JsonPropertyName("protocolVersion")] string ProtocolVersion,
    [property: JsonPropertyName("game")] GameIdentity Game,
    [property: JsonPropertyName("npc")] NpcIdentity Npc,
    [property: JsonPropertyName("player")] PlayerIdentity Player,
    [property: JsonPropertyName("relationship")] RelationshipContext? Relationship,
    [property: JsonPropertyName("world")] WorldContext? World,
    [property: JsonPropertyName("context")] ExtendedContext Context,
    [property: JsonPropertyName("interactionId")] string InteractionId
);

internal sealed record GameIdentity(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name
);

internal sealed record NpcIdentity(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("displayName")] string DisplayName,
    [property: JsonPropertyName("profileId")] string ProfileId
);

internal sealed record PlayerIdentity(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("displayName")] string DisplayName,
    [property: JsonPropertyName("message")] string Message
);

internal sealed record RelationshipContext(
    [property: JsonPropertyName("level")] double? Level,
    [property: JsonPropertyName("label")] string? Label,
    [property: JsonPropertyName("custom")] Dictionary<string, object> Custom
);

internal sealed record WorldContext(
    [property: JsonPropertyName("location")] string? Location,
    [property: JsonPropertyName("time")] string? Time,
    [property: JsonPropertyName("day")] int? Day,
    [property: JsonPropertyName("season")] string? Season,
    [property: JsonPropertyName("weather")] string? Weather,
    [property: JsonPropertyName("custom")] Dictionary<string, object> Custom
);

internal sealed record ExtendedContext(
    [property: JsonPropertyName("nearbyCharacters")] List<Dictionary<string, object>> NearbyCharacters,
    [property: JsonPropertyName("recentEvents")] List<object> RecentEvents,
    [property: JsonPropertyName("questState")] Dictionary<string, object> QuestState,
    [property: JsonPropertyName("custom")] Dictionary<string, object> Custom
);

internal sealed record ConversationResponse(
    [property: JsonPropertyName("protocolVersion")] string ProtocolVersion,
    [property: JsonPropertyName("success")] bool Success,
    [property: JsonPropertyName("npc")] string Npc,
    [property: JsonPropertyName("dialogue")] string Dialogue,
    [property: JsonPropertyName("emotion")] string? Emotion,
    [property: JsonPropertyName("confidence")] double? Confidence,
    [property: JsonPropertyName("facialExpression")] string? FacialExpression,
    [property: JsonPropertyName("relationshipDelta")] int RelationshipDelta,
    [property: JsonPropertyName("relationshipReason")] string? RelationshipReason,
    [property: JsonPropertyName("memoryState")] string? MemoryState,
    [property: JsonPropertyName("interactionId")] string? InteractionId,
    [property: JsonPropertyName("sentiment")] string? Sentiment,
    [property: JsonPropertyName("relationshipScore")] int? RelationshipScore,
    [property: JsonPropertyName("relationshipState")] string? RelationshipState,
    [property: JsonPropertyName("errorCode")] string? ErrorCode,
    [property: JsonPropertyName("error")] string? Error
);

internal sealed record PendingDialogue(
    string NpcId,
    string? Dialogue,
    string? Emotion,
    string? FacialExpression,
    int RelationshipDelta,
    string? RelationshipReason,
    string? MemoryState,
    string? Error
);
