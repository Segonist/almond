from discord import Interaction
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete, embed_generator

from database import update_mode, read_updatable_messages, Code


class Modes(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @has_permissions(administrator=True)
    @command(description="Змінює назву режиму гри")
    @rename(old_mode_name="з", new_mode_name="на")
    @describe(old_mode_name="Режим, назву якого потрібно змінити", new_mode_name="Нова назва режиму")
    @autocomplete(old_mode_name=mode_autocomplete)
    async def rename_game_mode(self, interaction: Interaction, old_mode_name: str, new_mode_name: str):
        guild = interaction.guild
        responce = update_mode(guild.id, old_mode_name, new_mode_name)
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

        new_mode_name = new_mode_name.lower()
        responce = read_updatable_messages(guild.id)
        if responce.code is not Code.SUCCESS:
            embed = embed_generator(
                "error", "Не вдалося редагувати оновлювані повідомлення.")
            await interaction.response.send_message(embed=embed)
            return
        for message in responce.data:
            if message["name"] == new_mode_name:
                message_id = message["message_id"]
                channel_id = message["channel_id"]
                channel = guild.get_channel(channel_id)
                msg = await channel.fetch_message(message_id)
                embed = msg.embeds[0].to_dict()
                new_title = embed["title"].replace(
                    old_mode_name, new_mode_name)
                new_embed = embed_generator(
                    "leaderboard", embed["description"], new_title, interaction)
                await msg.edit(embed=new_embed)


async def setup(bot: Bot):
    await bot.add_cog(Modes(bot))
