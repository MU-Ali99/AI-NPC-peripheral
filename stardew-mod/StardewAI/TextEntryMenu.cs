using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using StardewValley;
using StardewValley.Menus;

namespace StardewAI;

internal sealed class TextEntryMenu : IClickableMenu
{
    private readonly TextBox textBox;
    private readonly string title;
    private readonly Action<string> onSubmit;
    private bool completed;

    public TextEntryMenu(string npcName, Action<string> onSubmit)
        : base(Game1.uiViewport.Width / 2 - 320, Game1.uiViewport.Height / 2 - 110, 640, 220, true)
    {
        this.title = $"Talk to {npcName}";
        this.onSubmit = onSubmit;
        this.textBox = new TextBox(
            Game1.content.Load<Texture2D>("LooseSprites\\textBox"),
            null,
            Game1.smallFont,
            Game1.textColor
        )
        {
            X = this.xPositionOnScreen + 48,
            Y = this.yPositionOnScreen + 105,
            Width = this.width - 96,
            Selected = true
        };
        Game1.keyboardDispatcher.Subscriber = this.textBox;
    }

    public override void receiveKeyPress(Keys key)
    {
        if (key == Keys.Escape)
        {
            this.Close();
            return;
        }
        if (key == Keys.Enter)
        {
            string message = this.textBox.Text.Trim();
            if (message.Length > 0 && !this.completed)
            {
                this.completed = true;
                this.Close();
                this.onSubmit(message);
            }
            return;
        }
        // TextBox receives printable characters through keyboardDispatcher.
        // Do not forward them to Stardew's menu shortcuts (for example E).
    }

    private void Close()
    {
        this.textBox.Selected = false;
        if (ReferenceEquals(Game1.keyboardDispatcher.Subscriber, this.textBox))
            Game1.keyboardDispatcher.Subscriber = null;
        Game1.exitActiveMenu();
    }

    public override void draw(SpriteBatch b)
    {
        Game1.drawDialogueBox(this.xPositionOnScreen, this.yPositionOnScreen, this.width, this.height, false, true);
        Utility.drawTextWithShadow(b, this.title, Game1.dialogueFont, new Vector2(this.xPositionOnScreen + 48, this.yPositionOnScreen + 42), Game1.textColor);
        this.textBox.Draw(b);
        this.drawMouse(b);
    }
}
