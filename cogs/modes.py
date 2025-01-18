from discord import Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete, embed_generator

from database import update_mode, Code


class Modes(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Змінює назву режиму гри")
    @rename(old_mode_name="з", new_mode_name="на")
    @describe(old_mode_name="Режим, назву якого треба змінити", new_mode_name="Нова назва режиму")
    @autocomplete(old_mode_name=mode_autocomplete)
    async def rename_game_mode(self, interaction: Interaction, old_mode_name: str, new_mode_name: str):
        responce = update_mode(interaction.guild.id,
                               old_mode_name, new_mode_name)
        if responce.code == Code.ALREADY_EXISTS:
            embed = embed_generator(
                "error", f"Режим з назвою **{new_mode_name}** вже існує.")
        elif responce.code == Code.DOES_NOT_EXIST:
            embed = embed_generator(
                "error", f"Режиму з назвою **{old_mode_name}** не існує.")
        elif responce.code == Code.SUCCESS:
            embed = embed_generator(
                "success", f"Успішно змінено назву режиму **{old_mode_name}** на **{new_mode_name}**.")
        await interaction.response.send_message(embed=embed)
