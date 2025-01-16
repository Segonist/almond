from discord import Embed, Color, Interaction
from discord.app_commands import rename, describe, command, choices, Choice, autocomplete
from discord.ext.commands import Bot, Cog

from utils import mode_autocomplete

import database
from database import Response


class Leaderboard(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def win_form(number):
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

    @command(description="Показує таблицю лідерів")
    @rename(mode="режим", changable="оновлюване")
    @describe(changable="Визначає чи має повідомлення змінюватись під час додавання нових перемог (за замовчуванням ні)",
              mode="Режим гри з якого показати таблицю лідерів")
    @choices(changable=[
        Choice(name="так", value=1),
        Choice(name="ні", value=0),
    ])
    @autocomplete(mode=mode_autocomplete)
    async def show_leaderboard(self, interaction: Interaction, mode: str | None = None, changable: Choice[int] = 0):
        embed = Embed()
        responce = database.get_leaderboard(mode)
        if responce == Response.DOES_NOT_EXIST:
            embed.color = Color.brand_red()
            embed.title = "Помилка"
            embed.description = f"Режиму з назвою **{mode}** не існує."
            await interaction.response.send_message(embed=embed)
            return

        message = ""
        for i, player in enumerate(responce):
            user_id = player[0]
            wins = player[1]
            message += f"{i}. <@{user_id}> - **{
                wins}** {self.win_form(wins)}\n"

        embed.color = Color.blurple()
        if mode:
            embed.title = f"🏆 Таблиця лідерів режиму {mode} 🏆"
        else:
            embed.title = "🏆 Загальна таблиця лідерів 🏆"
        embed.description = message if message else "Дані відсутні."
        await interaction.response.send_message(embed=embed)
