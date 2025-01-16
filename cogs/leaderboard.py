from discord import Embed, Color, Interaction
from discord.app_commands import rename, describe, command, choices, Choice
from discord.ext.commands import Bot, Cog

import database


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
    @rename(type="тип", changable="оновлюване")
    @describe(type="Глобальна - бере під увагу переможців за весь час. (за замовчуванням), Сезонна - бере під увагу тільки переможців з цього сезону",
              changable="Визначає чи має повідомлення змінюватись під час додавання нових перемог (за замовчеванням ні)")
    @choices(type=[
        Choice(name="глобальна", value="global"),
        Choice(name="сезонна", value="seasonal"),
    ], changable=[
        Choice(name="так", value=1),
        Choice(name="ні", value=0),
    ])
    async def show_leaderboard(self, interaction: Interaction, type: Choice[str] = "global", changable: Choice[int] = 0):
        leaderboard = database.get_leaderboard(type)
        message = ""
        for i, player in enumerate(leaderboard):
            user_id = player[0]
            wins = player[1]
            message += f"{i}. <@{user_id}> - **{
                wins}** {self.win_form(wins)}\n"
        embed = Embed()
        embed.color = Color.blurple()
        embed.title = "🏆 Загальна таблиця лідерів 🏆"
        embed.description = message if message else "Дані відсутні."
        await interaction.response.send_message(embed=embed)
