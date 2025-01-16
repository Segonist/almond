from discord import Interaction
from discord.app_commands import Choice

import database


async def game_mode_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    game_modes = database.get_game_modes()
    return [
        Choice(name=mode[0], value=mode[0])
        for mode in game_modes if current.lower() in mode[0].lower()
    ]
