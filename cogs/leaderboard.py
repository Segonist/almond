from discord import Interaction
from discord.app_commands import (
    rename,
    describe,
    command,
    choices,
    Choice,
    autocomplete,
)
from discord.ext.commands import Cog, Bot

from utils import mode_autocomplete, embed_generator, EmbedType, generate_leaderboard

from database import create_updatable_message, Code


class Leaderboard(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(description="Показує таблицю лідерів")
    @rename(mode="режим", updatable="оновлюване")
    @describe(
        updatable="(опціональний) Чи має повідомлення змінюватись під час додавання нових перемог (за замовчуванням ні)",
        mode="(опціональний) Режим гри з якого показати таблицю лідерів",
    )
    @choices(
        updatable=[
            Choice(name="так", value=1),
            Choice(name="ні", value=0),
        ]
    )
    @autocomplete(mode=mode_autocomplete)
    async def leaderboard(
        self, interaction: Interaction, mode: str = None, updatable: Choice[int] = 0
    ):
        embed = await generate_leaderboard(interaction, mode)
        await interaction.response.send_message(embed=embed)
        if updatable:
            message = await interaction.original_response()
            guild_id = interaction.guild.id
            channel_id = interaction.channel.id
            message_id = message.id
            responce = await create_updatable_message(
                self.bot.async_session, guild_id, channel_id, message_id, mode
            )
            if responce.code is not Code.SUCCESS:
                embed = embed_generator(
                    EmbedType.ERROR, "Не вдалося створити оновлюване повідомлення."
                )
                await interaction.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Leaderboard(bot))
