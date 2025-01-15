from discord import Intents, Embed, Color, Member, Object, Interaction
from discord.app_commands import rename, describe, choices, Choice
from discord.ext.commands import Bot, Context, has_permissions, CheckFailure, CommandError, MissingPermissions

import database
from database import Response

from dotenv import dotenv_values

config = dotenv_values(".env")

PREFIX = config["PREFIX"]
TOKEN = config["TOKEN"]
ALLOWED_GUILD = Object(id=config["ALLOWED_GUILD"])

intents = Intents.default()
intents.message_content = True


class Almond(Bot):
    def __init__(self, *, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=ALLOWED_GUILD)
        await self.tree.sync(guild=ALLOWED_GUILD)


bot = Almond(command_prefix=PREFIX, intents=intents)


@bot.check
async def allowed_guild(context: Context):
    return context.guild.id == ALLOWED_GUILD.id


@bot.event
async def on_command_error(context: Context, error: CommandError):
    embed = Embed()
    if isinstance(error, CheckFailure):
        print(
            error, f"\nGuild {context.guild.name} ID: {context.guild.id}, owner's ID {context.guild.owner_id}")
        embed.color = Color.brand_red()
        embed.title = "Помилка"
        embed.description = f"Цей бот працює лише на визначеному сервері. Якщо ви хочете використати його на своєму сервері, сконтактуйтесь з [@Segonist](https://discord.com/users/491260818139119626)."
        await context.send(embed=embed)
    elif isinstance(error, MissingPermissions):
        embed.color = Color.brand_red()
        embed.title = "Помилка"
        embed.description = f"Цю команду може використовувати виключно адміністрація серверу."
        await context.send(embed=embed)
    else:
        embed.color = Color.brand_red()
        embed.title = "Помилка"
        embed.description = f"Яка? Хз. Скоріш за все щось що я не передбачив."
        await context.send(embed=embed)
        print(f"Unhandled error: {error}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@has_permissions(administrator=True)
@bot.tree.command(description="Додає новий режим гри")
@rename(name="назва")
@describe(name="Назва нового режиму")
async def add_game_mode(interaction: Interaction, name: str):
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
@bot.tree.command(description="Змінює назву режиму гри")
@rename(old_name="з", new_name="на")
@describe(old_name="Режим, назву якого треба змінити", new_name="Нова назва режиму")
async def edit_game_mode(interaction: Interaction, old_name: str, new_name: str):
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


@has_permissions(administrator=True)
@bot.tree.command(description="Додає перемогу гравцю")
@rename(user="гравець", game_mode="режим")
@describe(user="Гравець, якому треба додати перемогу", game_mode="Назва режиму гри")
async def add_victory(interaction: Interaction, user: Member, game_mode: str):
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


@bot.tree.command(description="Показує таблицю лідерів")
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
async def show_leaderboard(interaction: Interaction, type: Choice[str] = "global", changable: Choice[int] = 0):
    leaderboard = database.get_leaderboard(type)
    message = ""
    for i, player in enumerate(leaderboard):
        user_id = player[0]
        wins = player[1]
        message += f"{i}. <@{user_id}> - **{wins}** {win_form(wins)}\n"
    embed = Embed()
    embed.color = Color.blurple()
    embed.title = "🏆 Загальна таблиця лідерів 🏆"
    embed.description = message if message else "Дані відсутні."
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
