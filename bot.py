from discord import Intents, Embed, Color, Object
from discord.ext.commands import Bot, Context, CheckFailure, CommandError, MissingPermissions, is_owner

from dotenv import dotenv_values

from cogs.game_modes import Game_modes
from cogs.victories import Victories
from cogs.leaderboard import Leaderboard

config = dotenv_values(".env")

PREFIX = config["PREFIX"]
TOKEN = config["TOKEN"]
ALLOWED_GUILD = Object(id=config["ALLOWED_GUILD"])

intents = Intents.default()
intents.message_content = True


class Almond(Bot):
    def __init__(self, *, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        await self.add_cog(Game_modes(self))
        await self.add_cog(Victories(self))
        await self.add_cog(Leaderboard(self))
        self.tree.copy_global_to(guild=ALLOWED_GUILD)
        await self.tree.sync(guild=ALLOWED_GUILD)


bot = Almond(command_prefix=PREFIX, intents=intents)


@bot.check
async def allowed_guild(context: Context):
    return context.guild.id == ALLOWED_GUILD.id


@bot.event
async def on_command_error(context: Context, error: CommandError):
    embed = Embed()
    if isinstance(error, CheckFailure):
        print(
            error, f"\nGuild {context.guild.name} ID: {context.guild.id}, owner's ID {context.guild.owner_id}")
        embed.color = Color.brand_red()
        embed.title = "Помилка"
        embed.description = f"Цей бот працює лише на визначеному сервері. Якщо ви хочете використати його на своєму сервері, сконтактуйтесь з [@Segonist](https://discord.com/users/491260818139119626)."
        await context.send(embed=embed)
    elif isinstance(error, MissingPermissions):
        embed.color = Color.brand_red()
        embed.title = "Помилка"
        embed.description = f"Цю команду може використовувати виключно адміністрація серверу."
        await context.send(embed=embed)
    else:
        embed.color = Color.brand_red()
        embed.title = "Помилка"
        embed.description = f"Яка? Хз. Скоріш за все щось що я не передбачив."
        await context.send(embed=embed)
        print(f"Unhandled error: {error}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run(TOKEN)
