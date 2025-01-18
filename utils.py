from discord import Interaction, Color, Embed, Interaction
from discord.app_commands import Choice

from database import read_modes


async def mode_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    # reads modes from database, then compares them with current input. If there is some sort of match, it returns it
    modes = read_modes().data
    return [
        Choice(name=mode, value=mode)
        for mode in modes if current.lower() in mode.lower()
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
