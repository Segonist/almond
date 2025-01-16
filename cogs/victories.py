from discord import Embed, Color, Member, Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete

import database
from database import Response


class Victories(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Додає перемогу гравцю")
    @rename(user="гравець", mode="режим")
    @describe(user="Гравець, якому треба додати перемогу", mode="Назва режиму гри")
    @autocomplete(mode=mode_autocomplete)
    async def add_victory(self, interaction: Interaction, user: Member, mode: str):
        result = database.add_victory(user.id, mode)
        embed = Embed()
        if result == Response.SUCCESS:
            embed.color = Color.brand_green()
            embed.title = "Успіх"
            embed.description = f"Додано перемогу гравцю <@{
                user.id}> у режимі {mode}."
        else:
            embed.color = Color.brand_green()
            embed.title = "Помилка"
            embed.description = f"Щось пішло не так."
        await interaction.response.send_message(embed=embed)
