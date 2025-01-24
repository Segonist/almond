from discord import Intents, Object, Interaction, Color, Member, Guild
from discord.ext.commands import Bot, Context, CheckFailure, CommandError, MissingPermissions, check

from dotenv import dotenv_values

import logging

from utils import embed_generator, victory_form

from database import create_role, read_roles, read_data_for_roles

config = dotenv_values(".env")

PREFIX = config["PREFIX"]
TOKEN = config["TOKEN"]
ALLOWED_GUILDS = [Object(id=guild)
                  for guild in config["ALLOWED_GUILDS"].split(",")]

intents = Intents.default()
intents.members = True


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class Almond(Bot):
    def __init__(self, *, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.logger = logger

    async def create_roles(self, guild: Guild):
        # checks for users without roles and creates them
        roles = read_roles(guild.id)
        users_ids_with_roles = [role["user_id"] for role in roles.data]
        async for user in guild.fetch_members():
            if user.bot:
                continue
            if user.id not in users_ids_with_roles:
                new_role = await guild.create_role(name="0 перемог", color=Color.teal())
                await user.add_roles(new_role)
                create_role(guild.id, new_role.id, user.id)

    async def make_roles_names(self, guild: Guild):
        icons = {1: "🥇", 2: "🥈", 3: "🥉"}
        colors = {1: Color.gold(), 2: Color.greyple(),
                  3: Color.dark_orange()}
        result = read_data_for_roles(guild.id)
        leaderboard = result.data
        for i, user in enumerate(leaderboard, 1):
            role = guild.get_role(user["role_id"])
            name = f"{user["victories"]} {victory_form(user["victories"])}"
            if guild.premium_tier >= 2:
                icon = icons.get(i, "")
            else:
                icon = None
            color = colors.get(i, Color.teal())
            if role:
                await role.edit(name=name, display_icon=icon, color=color)

    async def on_member_join(self, member: Member):
        await self.create_roles(member.guild)
        await self.make_roles_names(member.guild)

    async def on_guild_join(self, guild: Guild):
        await self.create_roles(guild)
        await self.make_roles_names(guild)

    async def setup_hook(self):
        await bot.load_extension("cogs.leaderboard")
        await bot.load_extension("cogs.modes")
        await bot.load_extension("cogs.victories")
        await bot.load_extension("cogs.help")

        for guild in ALLOWED_GUILDS:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        self.logger.info(f"Бот увійшов за {self.user.name} ID: {self.user.id}")
        self.logger.info("-------------------")

        for guild in self.guilds:
            await self.create_roles(guild)
            await self.make_roles_names(guild)

    # global check that allows bot to work only on specified servers
    @check
    async def allowed_guilds(self, context: Context):
        for guild in ALLOWED_GUILDS:
            if context.guild.id == guild.id:
                return True
        return False

    async def on_command_error(self, context: Context, error: CommandError):
        if isinstance(error, CheckFailure):
            self.logger.error(
                error, f"\nСервер {context.guild.name} ID: {context.guild.id}, ID власника {context.guild.owner_id}, ID користувача, що викликав команду {context.author.id}")
            embed = embed_generator(
                "error", "Цей бот працює лише на визначеномих серверах. Якщо ви хочете використати його на своєму сервері, сконтактуйтесь з [@Segonist](https://discord.com/users/491260818139119626).")
        elif isinstance(error, MissingPermissions):
            embed = embed_generator(
                "error", "Цю команду може використовувати виключно адміністрація серверу.")
        else:
            self.logger.error(
                f"Сервер ${context.guild.name}. Необроблена помилка: {error}")
            embed = embed_generator("error", "Щось пішло не так.")
        await context.send(embed=embed)

    async def on_interaction(self, interaction: Interaction):
        command = interaction.command.name
        self.logger.info(
            f"Виконано команду {command} на сервері {interaction.guild.name} #{interaction.guild.id} в каналі {interaction.channel.name} #{interaction.channel.id} користувачем {interaction.user} #{interaction.user.id}")


bot = Almond(command_prefix=PREFIX, intents=intents)

bot.run(TOKEN)
