using StardewModdingAPI.Utilities;

namespace StardewAI;

internal sealed class ModConfig
{
    public KeybindList ConversationKey { get; set; } = KeybindList.Parse("LeftAlt + D1");
    public string BridgeUrl { get; set; } = "http://127.0.0.1:8765/v1/conversation";
    public int RequestTimeoutSeconds { get; set; } = 90;
    public float InteractionDistanceTiles { get; set; } = 4f;
}

