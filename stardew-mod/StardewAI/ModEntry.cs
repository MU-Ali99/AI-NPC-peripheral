using System.Collections.Concurrent;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace StardewAI;

internal sealed class ModEntry : Mod
{
    private readonly ConcurrentQueue<PendingDialogue> pendingDialogues = new();
    private readonly JsonSerializerOptions jsonOptions = new(JsonSerializerDefaults.Web);
    private HttpClient httpClient = null!;
    private ModConfig config = null!;
    private bool requestInProgress;

    public override void Entry(IModHelper helper)
    {
        this.config = helper.ReadConfig<ModConfig>();
        this.httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(this.config.RequestTimeoutSeconds) };
        helper.Events.Input.ButtonsChanged += this.OnButtonsChanged;
        helper.Events.GameLoop.UpdateTicked += this.OnUpdateTicked;
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => this.requestInProgress = false;
        this.Monitor.Log($"Stardew AI loaded. Conversation key: {this.config.ConversationKey}; bridge: {this.config.BridgeUrl}", LogLevel.Info);
    }

    private void OnButtonsChanged(object? sender, ButtonsChangedEventArgs e)
    {
        if (!Context.IsWorldReady || !this.config.ConversationKey.JustPressed() || Game1.activeClickableMenu is not null)
            return;
        if (Context.IsMultiplayer)
        {
            Game1.addHUDMessage(new HUDMessage("AI conversations currently support single-player games only.", HUDMessage.error_type));
            return;
        }
        if (this.requestInProgress)
        {
            Game1.addHUDMessage(new HUDMessage("An AI conversation is already processing.", HUDMessage.error_type));
            return;
        }

        NPC? npc = this.FindNearestNpc();
        if (npc is null)
        {
            Game1.addHUDMessage(new HUDMessage("No NPC is close enough to talk to.", HUDMessage.error_type));
            return;
        }

        this.Monitor.Log($"Hotkey detected; target NPC: {npc.Name}", LogLevel.Info);
        Game1.activeClickableMenu = new TextEntryMenu(npc.displayName, message => this.BeginConversation(npc, message));
    }

    private NPC? FindNearestNpc()
    {
        Vector2 playerTile = Game1.player.Tile;
        return Game1.currentLocation.characters
            .Where(npc => npc.IsVillager && Vector2.Distance(playerTile, npc.Tile) <= this.config.InteractionDistanceTiles)
            .OrderBy(npc => Vector2.DistanceSquared(playerTile, npc.Tile))
            .FirstOrDefault();
    }

    private void BeginConversation(NPC npc, string message)
    {
        int hearts = Game1.player.friendshipData.TryGetValue(npc.Name, out Friendship? friendship)
            ? friendship.Points / 250
            : 0;
        string weather = Game1.IsRainingHere(Game1.currentLocation) ? "rain" : Game1.isSnowing ? "snow" : "clear";
        string time = $"{Game1.timeOfDay / 100:D2}:{Game1.timeOfDay % 100:D2}";
        List<Dictionary<string, object>> nearbyCharacters = Game1.currentLocation.characters
            .Where(character => character.IsVillager && character.Name != npc.Name && Vector2.Distance(Game1.player.Tile, character.Tile) <= 8f)
            .Select(character => new Dictionary<string, object>
            {
                ["id"] = character.Name,
                ["displayName"] = character.displayName
            })
            .ToList();
        var request = new ConversationRequest(
            "2.0",
            new GameIdentity("stardew_valley", "Stardew Valley"),
            new NpcIdentity(npc.Name, npc.displayName, $"stardew_valley.{npc.Name.ToLowerInvariant()}"),
            new PlayerIdentity(Game1.player.UniqueMultiplayerID.ToString(), Game1.player.Name, message),
            new RelationshipContext(Math.Clamp(hearts, 0, 14), "friendship_hearts", new Dictionary<string, object>()),
            new WorldContext(Game1.currentLocation.NameOrUniqueName, time, Game1.dayOfMonth, Game1.currentSeason, weather, new Dictionary<string, object>()),
            new ExtendedContext(nearbyCharacters, new List<object>(), new Dictionary<string, object>(), new Dictionary<string, object>
            {
                ["adapter"] = "AINPCPeripheral.StardewAI",
                ["singlePlayer"] = !Context.IsMultiplayer
            })
        );

        this.requestInProgress = true;
        Game1.activeClickableMenu = new WaitingMenu(npc.displayName);
        this.Monitor.Log($"Sending request for {npc.Name}", LogLevel.Info);
        _ = this.SendConversationAsync(request);
    }

    private async Task SendConversationAsync(ConversationRequest request)
    {
        try
        {
            using HttpResponseMessage response = await this.httpClient.PostAsJsonAsync(this.config.BridgeUrl, request, this.jsonOptions).ConfigureAwait(false);
            response.EnsureSuccessStatusCode();
            ConversationResponse? result = await response.Content.ReadFromJsonAsync<ConversationResponse>(this.jsonOptions).ConfigureAwait(false);
            if (result is null)
                throw new InvalidDataException("NPCBridge returned an empty response.");
            this.pendingDialogues.Enqueue(result.Success
                ? new PendingDialogue(request.Npc.Id, result.Dialogue, result.Emotion, result.FacialExpression, result.RelationshipDelta, result.RelationshipReason, result.MemoryState, null)
                : new PendingDialogue(request.Npc.Id, null, null, null, 0, null, null, result.Error ?? "NPCBridge could not generate dialogue."));
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException or JsonException or InvalidDataException)
        {
            this.Monitor.Log($"NPCBridge request failed: {ex.Message}", LogLevel.Error);
            this.pendingDialogues.Enqueue(new PendingDialogue(request.Npc.Id, null, null, null, 0, null, null, "AI conversation service is unavailable."));
        }
    }

    private void OnUpdateTicked(object? sender, UpdateTickedEventArgs e)
    {
        while (this.pendingDialogues.TryDequeue(out PendingDialogue? result))
        {
            this.requestInProgress = false;
            if (result.Error is not null)
            {
                Game1.exitActiveMenu();
                Game1.addHUDMessage(new HUDMessage(result.Error, HUDMessage.error_type));
                continue;
            }
            this.Monitor.Log($"Response received for {result.NpcId}", LogLevel.Info);
            NPC? npc = Game1.getCharacterFromName(result.NpcId);
            string speaker = npc?.displayName ?? result.NpcId;
            if (npc is not null && result.RelationshipDelta != 0)
            {
                Game1.player.changeFriendship(result.RelationshipDelta, npc);
                this.Monitor.Log($"Relationship changed for {result.NpcId}: {result.RelationshipDelta:+#;-#;0} ({result.RelationshipReason}); memory={result.MemoryState}", LogLevel.Info);
            }
            string expression = string.IsNullOrWhiteSpace(result.FacialExpression) ? "" : $"*{speaker} wears {result.FacialExpression}.*\n";
            Game1.drawObjectDialogue($"{expression}{speaker}: {result.Dialogue}");
        }
    }
}
