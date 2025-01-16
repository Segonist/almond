from discord import Embed, Color, Member, Interaction
from discord.app_commands import rename, describe, command
from discord.ext.commands import Bot, Cog, has_permissions

import database
from database import Response


class Victories(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Додає перемогу гравцю")
    @rename(user="гравець", game_mode="режим")
    @describe(user="Гравець, якому треба додати перемогу", game_mode="Назва режиму гри")
    async def add_victory(self, interaction: Interaction, user: Member, game_mode: str):
        result = database.add_victory(user.id, game_mode)
        embed = Embed()
        if result == Response.DOES_NOT_EXIST:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режиму з назвою **{game_mode}** не існує."
        elif result == Response.SUCCESS:
            embed.color = Color.brand_green()
            embed.title = "Успіх"
            embed.description = f"Додано перемогу гравцю <@{
                user.id}> у режимі {game_mode}."
        await interaction.response.send_message(embed=embed)
