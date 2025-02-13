import os

from discord import Intents, Object, Interaction, Color, Member, Guild, InteractionType, CustomActivity
from discord.ext.commands import Bot, Context, CheckFailure, CommandError, MissingPermissions, check

from dotenv import load_dotenv

import logging.handlers

from utils import embed_generator, victory_form

from database import read_leaderboard, create_role, read_roles, delete_role, read_data_for_roles

load_dotenv()

ALLOWED_GUILDS = [Object(id=guild)
                  for guild in os.getenv("ALLOWED_GUILDS").split(",")]


intents = Intents.default()
intents.members = True


logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Almond(Bot):
    def __init__(self, *, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.logger = logging.getLogger("discord")

    def return_on_unallowed_guild(self, guild: Guild):
        if guild not in ALLOWED_GUILDS:
            return

    async def create_guild_roles(self, guild: Guild):
        self.return_on_unallowed_guild(guild)
        
        roles = await read_roles(guild.id)
        for role in roles:
            member = guild.get_member(role["user_id"])
            role = guild.get_role(role["role_id"])
            # check if member is in guild
            if member not in guild.members:
                await delete_role(guild.id, role["role_id"])
            # check if role exists
            if not role:
                await delete_role(guild.id, role["role_id"])
            # check if role is assigned to the user
            if not member.get_role(role.id):
                await member.add_roles(role)

        victories = await read_leaderboard(guild.id)
        users_ids_with_victories = [victory["user_id"] for victory in victories]
        roles = await read_roles(guild.id)
        users_ids_with_roles = [role["user_id"] for role in roles]
        # compare two lists, if there are diffs, create roles for those diffs


    async def create_guild_role(self, user: Member):
        guild = user.guild
        new_role = await guild.create_role(name="0 перемог", color=Color.teal())
        await user.add_roles(new_role)
        await create_role(guild.id, new_role.id, user.id)

    async def make_roles_names(self, guild: Guild):
        self.return_on_unallowed_guild(guild)
        if guild not in ALLOWED_GUILDS:
            return
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
        pass
        # await self.create_roles(member.guild)
        # await self.make_roles_names(member.guild)

    async def on_guild_join(self, guild: Guild):
        pass
        # await self.create_roles(guild)
        # await self.make_roles_names(guild)

    async def setup_hook(self):
        await bot.load_extension("cogs.leaderboard")
        await bot.load_extension("cogs.modes")
        await bot.load_extension("cogs.victories")
        await bot.load_extension("cogs.help")

        for guild in ALLOWED_GUILDS:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        self.logger.info(f"Bot logged in as {
                         self.user.name} ID: {self.user.id}")
        self.logger.info("-------------------")

        for guild in self.guilds:
            pass
            # await self.create_roles(guild)
            # await self.make_roles_names(guild)

        activity = CustomActivity(
            name="\U0001F4DD Підраховує перемоги")
        await self.change_presence(activity=activity)

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
                error, f"\nBot command used on server that is not on the allowed list: {context.guild.name} ID: {context.guild.id}")
            embed = embed_generator(
                "error", "Цей бот працює лише на визначеномих серверах. Якщо ви хочете використати його на своєму сервері, сконтактуйтесь з [@Segonist](https://discord.com/users/491260818139119626).")
        elif isinstance(error, MissingPermissions):
            embed = embed_generator(
                "error", "Цю команду може використовувати виключно адміністрація серверу.")
        else:
            self.logger.error(
                f"Guild {context.guild.name} #{context.guild.id}. Unhandled exeption: {error}")
            embed = embed_generator("error", "Щось пішло не так.")
        await context.send(embed=embed)

    async def on_interaction(self, interaction: Interaction):
        if interaction.type is InteractionType.application_command:
            command = interaction.command
            options = interaction.data.get("options", None)
            parameters = "with no parameters"
            if options:
                parameters = "with parameters " + ", ".join(
                    [f"{command["name"]}: {command["value"]}" for command in options])
            self.logger.info(
                f"""Excucuted command {command.name} {parameters}
Guild {interaction.guild.name} #{interaction.guild.id}
Channel {interaction.channel.name} #{interaction.channel.id}
User {interaction.user} #{interaction.user.id}""")


bot = Almond(command_prefix=os.getenv("PREFIX"), intents=intents)

bot.run(os.getenv("TOKEN"))
