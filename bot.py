from discord import Intents, Object
from discord.ext.commands import Bot, Context, CheckFailure, CommandError, MissingPermissions

from dotenv import dotenv_values

from cogs.modes import Modes
from cogs.victories import Victories
from cogs.leaderboard import Leaderboard

from utils import embed_generator

config = dotenv_values(".env")

PREFIX = config["PREFIX"]
TOKEN = config["TOKEN"]
ALLOWED_SERVER = Object(id=config["ALLOWED_SERVER"])

intents = Intents.default()
intents.message_content = True


class Almond(Bot):
    def __init__(self, *, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        await self.add_cog(Modes(self))
        await self.add_cog(Victories(self))
        await self.add_cog(Leaderboard(self))
        self.tree.copy_global_to(guild=ALLOWED_SERVER)
        await self.tree.sync(guild=ALLOWED_SERVER)


bot = Almond(command_prefix=PREFIX, intents=intents)


@bot.check
async def allowed_server(context: Context):
    return context.guild.id == ALLOWED_SERVER.id


@bot.event
async def on_command_error(context: Context, error: CommandError):
    if isinstance(error, CheckFailure):
        print(
            error, f"\nServer {context.guild.name} ID: {context.guild.id}, owner's ID {context.guild.owner_id}")
        embed = embed_generator(
            "error", "Цей бот працює лише на визначеному сервері. Якщо ви хочете використати його на своєму сервері, сконтактуйтесь з [@Segonist](https://discord.com/users/491260818139119626).")
    elif isinstance(error, MissingPermissions):
        embed = embed_generator(
            "error", "Цю команду може використовувати виключно адміністрація серверу.")
    else:
        print(f"Unhandled error: {error}")
        embed = embed_generator("error", "Щось пішло не так.")
    await context.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run(TOKEN)
