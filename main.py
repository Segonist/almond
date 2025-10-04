from discord import (
    Interaction,
    InteractionType,
    Intents,
    Object,
    __version__,
    CustomActivity,
)
from discord.ext.commands import (
    when_mentioned_or,
    Bot,
    Context,
    MissingPermissions,
    BotMissingPermissions,
    CommandError,
)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

from logger import logger
import os
import platform

from database.models import Base

from utils import embed_generator, EmbedType

intents = Intents.default()
intents.message_content = True

load_dotenv()

PREFIX = "&&"
TOKEN = os.getenv("TOKEN")
# Change this to quering guilds that use bot from db
GUILDS = [Object(id=guild) for guild in os.getenv("GUILDS").split(",")]


class Almond(Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=when_mentioned_or(PREFIX),
            intents=intents,
            help_command=None,
        )
        self.async_session: sessionmaker[AsyncSession] | None = None
        self.logger = logger

    async def init_db(self) -> None:
        dialect = "mysql"
        driver = "aiomysql"
        username = os.getenv("MARIADB_USER")
        password = os.getenv("MARIADB_PASSWORD")
        host = os.getenv("MARIADB_HOST")
        port = os.getenv("MARIADB_PORT")
        database = os.getenv("MARIADB_DATABASE")
        database_url = (
            f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"
        )

        engine = create_async_engine(database_url)

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        self.async_session = async_session

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )

        await self.init_db()
        await self.load_cogs()

    async def on_ready(self) -> None:
        for guild in GUILDS:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

        activity = CustomActivity(name="\U0001f4dd Підраховує перемоги")
        await self.change_presence(activity=activity)

    async def on_interaction(self, interaction: Interaction):
        if interaction.type is InteractionType.application_command:
            executed_command = interaction.command.name
            options = interaction.data.get("options", None)
            parameters = "with no parameters"
            if options:
                parameters = "with parameters " + ", ".join(
                    [f"{command['name']}: {command['value']}" for command in options]
                )
            self.logger.info(
                f"Executed {executed_command} command {parameters} in {interaction.guild.name} #{interaction.guild.id} (channel {interaction.channel} #{interaction.channel.id}) by {interaction.user} #{interaction.user.id}"
            )

    async def on_command_completion(self, context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        self.logger.info(
            f"Executed {executed_command} command in {context.guild.name} #{context.guild.id} (channel {context.channel} #{context.channel.id}) by {context.author} (ID: {context.author.id})"
        )

    async def on_command_error(self, context: Context, error: CommandError):
        if isinstance(error, MissingPermissions):
            embed = embed_generator(
                EmbedType.ERROR,
                "В тебе нема потрібних прав до виклику цієї команди.",
            )
        elif isinstance(error, BotMissingPermissions):
            embed = embed_generator(
                EmbedType.ERROR,
                "В мене нема потрібних прав до виконання цієї команди.",
            )
            await context.send(embed=embed)
        else:
            self.logger.error(
                f"Guild {context.guild.name} #{context.guild.id}. Unhandled exeption: {error}"
            )
            embed = embed_generator(EmbedType.ERROR, "Щось пішло не так.")
        await context.send(embed=embed)


bot = Almond()
bot.run(TOKEN)
