from discord import Interaction, Color, Embed, Interaction
from discord.app_commands import Choice

from time import time

from database import read_modes

mode_cache = {}


async def mode_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    guild_id = interaction.guild.id
    now = time()

    # 10 seconds just so it won't make db request every time user types
    if guild_id in mode_cache and now - mode_cache[guild_id]['timestamp'] < 10:
        modes = mode_cache[guild_id]['data']
    else:
        modes = read_modes(guild_id).data
        mode_cache[guild_id] = {'data': modes, 'timestamp': now}

    return [
        Choice(name=mode["name"], value=mode["name"])
        for mode in modes if current.lower() in mode["name"].lower()
    ]


def embed_generator(type: str, description: str, title: str | None = None, interaction: Interaction | None = None) -> Embed:
    embed = Embed(description=description, title=title)
    match type:
        case "error":
            embed.color = Color.brand_red()
            embed.title = "Помилка"
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
