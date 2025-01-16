from discord import Embed, Color, Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete

import database
from database import Response


class Modes(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Змінює назву режиму гри")
    @rename(old_mode_name="з", new_mode_name="на")
    @describe(old_mode_name="Режим, назву якого треба змінити", new_mode_name="Нова назва режиму")
    @autocomplete(old_mode_name=mode_autocomplete)
    async def edit_game_mode(self, interaction: Interaction, old_mode_name: str, new_mode_name: str):
        result = database.edit_mode(old_mode_name, new_mode_name)
        embed = Embed()
        if result == Response.ALREADY_EXCISTS:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режим з назвою **{
                new_mode_name}** вже існує."
        elif result == Response.DOES_NOT_EXIST:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режиму з назвою **{
                old_mode_name}** не існує."
        elif result == Response.SUCCESS:
            embed.color = Color.brand_green()
            embed.title = "Успіх"
            embed.description = f"Успішно змінено назву режиму **{
                old_mode_name}** на **{new_mode_name}**."
        await interaction.response.send_message(embed=embed)
