from discord import Embed, Color, Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import game_mode_autocomplete

import database
from database import Response


class Game_modes(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Додає новий режим гри")
    @rename(name="назва")
    @describe(name="Назва нового режиму")
    async def add_game_mode(self, interaction: Interaction, name: str):
        result = database.add_game_mode(name)
        embed = Embed()
        if result == Response.ALREADY_EXCISTS:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режим **{name}** вже існує."
        elif result == Response.SUCCESS:
            embed.color = Color.brand_green()
            embed.title = "Успіх"
            embed.description = f"Успішно додано режим гри **{name}**."
        await interaction.response.send_message(embed=embed)

    @has_permissions(administrator=True)
    @command(description="Змінює назву режиму гри")
    @rename(old_name="з", new_name="на")
    @describe(old_name="Режим, назву якого треба змінити", new_name="Нова назва режиму")
    @autocomplete(old_name=game_mode_autocomplete)
    async def edit_game_mode(self, interaction: Interaction, old_name: str, new_name: str):
        result = database.edit_game_mode(old_name, new_name)
        embed = Embed()
        if result == Response.ALREADY_EXCISTS:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режим з назвою **{new_name}** вже існує."
        elif result == Response.DOES_NOT_EXIST:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режиму з назвою **{old_name}** не існує."
        elif result == Response.SUCCESS:
            embed.color = Color.brand_green()
            embed.title = "Успіх"
            embed.description = f"Успішно змінено назву режиму **{
                old_name}** на **{new_name}**."
        await interaction.response.send_message(embed=embed)
