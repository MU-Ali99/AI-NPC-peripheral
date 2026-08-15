using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using StardewValley;
using StardewValley.Menus;

namespace StardewAI;

internal sealed class WaitingMenu : IClickableMenu
{
    private readonly string message;

    public WaitingMenu(string npcName)
        : base(Game1.uiViewport.Width / 2 - 280, Game1.uiViewport.Height / 2 - 80, 560, 160, false)
    {
        this.message = $"{npcName} is thinking...";
    }

    public override void receiveKeyPress(Keys key)
    {
        // The request remains active. Keeping this menu open also keeps normal
        // single-player world updates paused until a response or error arrives.
    }

    public override void draw(SpriteBatch b)
    {
        Game1.drawDialogueBox(this.xPositionOnScreen, this.yPositionOnScreen, this.width, this.height, false, true);
        Vector2 size = Game1.dialogueFont.MeasureString(this.message);
        Vector2 position = new(this.xPositionOnScreen + (this.width - size.X) / 2, this.yPositionOnScreen + 54);
        Utility.drawTextWithShadow(b, this.message, Game1.dialogueFont, position, Game1.textColor);
        this.drawMouse(b);
    }
}
