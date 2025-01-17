from discord import Interaction, Color, Embed, Interaction
from discord.app_commands import Choice

from database import read_modes


async def mode_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
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
            server_name = interaction.guild.name
            server_icon = interaction.guild.icon
            if server_icon:
                server_icon = server_icon.url
            embed.set_footer(text=server_name, icon_url=server_icon)

    return embed
