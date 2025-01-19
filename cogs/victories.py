from discord import Member, Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete, embed_generator

from database import create_victory, delete_last_victory, Code


class Victories(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Додає перемогу гравцю")
    @rename(user="гравець", mode="режим")
    @describe(user="Гравець, якому треба додати перемогу", mode="Назва режиму гри")
    @autocomplete(mode=mode_autocomplete)
    async def victory(self, interaction: Interaction, user: Member, mode: str):
        responce = create_victory(interaction.guild.id, user.id, mode)
        if responce.code == Code.SUCCESS:
            embed = embed_generator(
                "success", f"Додано перемогу гравцю <@{user.id}> у режимі **{mode}**.")
        else:
            embed = embed_generator("error", "Щось пішло не так.")
        await interaction.response.send_message(embed=embed)

    @has_permissions(administrator=True)
    @command(description="Видаляє останню додану перемогу")
    async def remove_last_victory(self, interaction: Interaction):
        responce_data = delete_last_victory(interaction.guild.id).data
        embed = embed_generator(
            "success", f"Видалено перемогу гравцю <@{responce_data['discord_user_id']}> у режимі **{responce_data['name']}**.")
        await interaction.response.send_message(embed=embed)
