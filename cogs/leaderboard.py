from discord import Interaction
from discord.app_commands import rename, describe, command, choices, Choice, autocomplete
from discord.ext.commands import Bot, Cog

from utils import mode_autocomplete, embed_generator

from database import read_leaderboard, create_updatable_message, Code


class Leaderboard(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def victory_form(number):
        number = int(str(number)[-2:])
        if number >= 11 and number <= 19:
            return "перемог"
        number = int(str(number)[-1:])
        if number == 0:
            return "перемог"
        elif number == 1:
            return "перемога"
        elif number >= 2 and number <= 4:
            return "перемоги"
        elif number >= 5 and number <= 9:
            return "перемог"

    @staticmethod
    def generate_leaderboard(interaction: Interaction, mode: str = None):
        responce = read_leaderboard(interaction.guild.id, mode)
        if responce.code == Code.DOES_NOT_EXIST:
            embed = embed_generator(
                "error", f"Режиму з назвою **{mode}** не існує.")
            return embed

        message = ""
        if not responce:
            message = "Дані відсутні."
        else:
            for i, player in enumerate(responce.data, 1):
                user_id = player["discord_user_id"]
                victories = player["victories"]
                message += f"{i}. <@{user_id}> - **{
                    victories}** {Leaderboard.victory_form(victories)}\n"

        if mode:
            title = f"🏆 Таблиця лідерів режиму {mode} 🏆"
        else:
            title = "🏆 Загальна таблиця лідерів 🏆"
        embed = embed_generator("leaderboard", message, title, interaction)
        return embed

    @command(description="Показує таблицю лідерів")
    @rename(mode="режим", updatable="оновлюване")
    @describe(updatable="Визначає чи має повідомлення змінюватись під час додавання нових перемог (за замовчуванням ні)",
              mode="Режим гри з якого показати таблицю лідерів")
    @choices(updatable=[
        Choice(name="так", value=1),
        Choice(name="ні", value=0),
    ])
    @autocomplete(mode=mode_autocomplete)
    async def leaderboard(self, interaction: Interaction, mode: str | None = None, updatable: Choice[int] = 0):
        embed = self.generate_leaderboard(interaction, mode)
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        if updatable:
            guild_id = interaction.guild.id
            channel_id = interaction.channel.id
            message_id = message.id
            responce = create_updatable_message(
                guild_id, channel_id, message_id, mode)
            if responce.code is not Code.SUCCESS:
                embed = embed_generator(
                    "error", "Не вдалося створити оновлюване повідомлення.")
                await interaction.response.send_message(embed=embed)
