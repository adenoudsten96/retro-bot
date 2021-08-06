from discord.ext.commands import Bot
from discord_components import DiscordComponents, Button

bot = Bot(command_prefix = "/")


@bot.event
async def on_ready():
    DiscordComponents(bot)
    print(f"Logged in as {bot.user}!")


@bot.command()
async def button(ctx):
    await ctx.send(
        "Hello, World!",
        components = [
            Button(label = "WOW button!")
        ]
    )

    interaction = await bot.wait_for("button_click", check = lambda i: i.component.label.startswith("WOW"))
    await interaction.respond(content = "Button clicked!")


bot.run("NzQ1OTc4MDEyNjkyMTE5NjQy.Xz5oKQ.RMgs8xbbihrZR5E6VfeC8YRDmHU")