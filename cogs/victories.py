from discord import Member, Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete, embed_generator

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
        if result == Response.SUCCESS:
            embed = embed_generator(
                "success", f"Додано перемогу гравцю <@{user.id}> у режимі {mode}.")
        else:
            embed = embed_generator("error", "Щось пішло не так.")
        await interaction.response.send_message(embed=embed)

    @has_permissions(administrator=True)
    @command(description="Видаляє останню додану перемогу")
    async def remove_last_victory(self, interaction: Interaction):
        result = database.remove_last_victory()
        embed = embed_generator(
            "success", f"Видалено перемогу гравцю <@{result[0]}> у режимі {result[1]}.")
        await interaction.response.send_message(embed=embed)
