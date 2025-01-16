from discord import Interaction
from discord.app_commands import Choice

import database


async def mode_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    modes = database.get_modes()
    return [
        Choice(name=mode[0], value=mode[0])
        for mode in modes if current.lower() in mode[0].lower()
    ]
