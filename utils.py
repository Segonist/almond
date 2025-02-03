from discord import Interaction, Color, Embed, Interaction
from discord.app_commands import Choice

from time import time

from database import read_modes, read_leaderboard, Code

mode_cache = {}


async def mode_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    guild_id = interaction.guild.id
    now = time()

    # 10 seconds just so it won't make db request every time user types
    if guild_id in mode_cache and now - mode_cache[guild_id]['timestamp'] < 10:
        modes = mode_cache[guild_id]['data']
    else:
        responce = await read_modes(guild_id)
        if responce is Code.DOES_NOT_EXIST:
            return
        modes = [mode["name"] for mode in responce.data]
        mode_cache[guild_id] = {'data': modes, 'timestamp': now}

    return [
        Choice(name=mode, value=mode)
        for mode in modes if current.lower() in mode.lower()
    ]


def embed_generator(type: str, description: str, title: str | None = None, interaction: Interaction | None = None) -> Embed:
    embed = Embed(description=description, title=title)
    match type:
        case "help":
            embed.color = Color.dark_grey()
            embed.title = "Допомога"
        case "error":
            embed.color = Color.brand_red()
            embed.title = "Помилка"
        case "warning":
            embed.color = Color.yellow()
            embed.title = "Увага"
        case "success":
            embed.color = Color.brand_green()
            embed.title = "Успіх"
        case "leaderboard":
            embed.color = Color.blurple()
            guild_name = interaction.guild.name
            guild_icon = interaction.guild.icon
            if guild_icon:
                guild_icon = guild_icon.url
            embed.set_footer(text=guild_name, icon_url=guild_icon)

    return embed


def victory_form(number: int) -> str:
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


async def generate_leaderboard(interaction: Interaction, mode: str = None) -> Embed:
    responce = await read_leaderboard(interaction.guild.id, mode)
    if responce.code == Code.DOES_NOT_EXIST:
        embed = embed_generator(
            "error", f"Режиму з назвою **{mode}** не існує.")
        return embed

    message = ""
    if not responce.data:
        message = "Дані відсутні."
    else:
        for i, player in enumerate(responce.data, 1):
            user_id = player["user_id"]
            victories = player["victories"]
            message += f"{i}. <@{user_id}> - **{
                victories}** {victory_form(victories)}\n"

    if mode:
        title = f"🏆 Таблиця лідерів режиму {mode} 🏆"
    else:
        title = "🏆 Загальна таблиця лідерів 🏆"
    embed = embed_generator("leaderboard", message, title, interaction)
    return embed
