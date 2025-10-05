from discord import Interaction
from discord.app_commands import rename, describe, command, choices, Choice
from discord.ext.commands import Cog, Bot

from utils import embed_generator, EmbedType


class Help(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.leaderboard = """# leaderboard
**Виводить таблицю лідерів**
## Параметри
- `режим` - Таблиця лідерів буде брати під увагу перемоги з вказаного режиму (опціональний)
- `оновлюване` - Якщо так, повідомлення буде оновлюватись під час додавання нових перемог (опціональний). *На оновлення повідомлення може піти деякий час*
"""
        self.victory = """# victory
**Додає перемогу в таблицю лідерів**
## Параметри
- `режим` - Режим гри, в якому була здобута перемога. *Якщо поданого режиму не існує, його буде створено*
- `гравець` - Гравець, якому належить перемога
"""
        self.rename_game_mode = """# rename_game_mode
**Змінює назву режиму гри**
## Параметри
- `з` - Поточна назва режиму
- `на` - Нова назва режиму
"""
        self.remove_last_victory = """# remove_last_victory
**Видаляє найпізнішу додану перемогу**
"""
        self.vc_select_random_user = """# vc_select_random_user
**Вибирає випадкову особу з голосового чату, в якому знаходиться людина що киликає команду**
## Параметри
- `автор` - Якщо так, людина що викликає команду буде включена в жеребкування (опціональний)
"""
        self.split_vc_into_teams = """# split_vc_into_teams
**Поділяє осіб з голосового чату в якому знаходиться людина що викликає команду на (в міру можливості) рівні команди**
## Параметри
- `команди` - Кількість команд. *Команди будуть мати різну кількість осіб якщо кільуість осіб не можна поділити на кількість команд без залишку*
- `автор` - Якщо так, людина що викликає команду буде включена в жеребкування (опціональний)
"""

    @command(description="Допомога по боту")
    @rename(command="команда")
    @describe(command="(опціональний) Команда, по якій потрібна допомога")
    @choices(
        command=[
            Choice(name="leaderboard", value="leaderboard"),
            Choice(name="victory", value="victory"),
            Choice(name="rename_game_mode", value="rename_game_mode"),
            Choice(name="remove_last_victory", value="remove_last_victory"),
            Choice(name="vc_select_random_user", value="vc_select_random_user"),
            Choice(name="split_vc_into_teams", value="split_vc_into_teams"),
        ]
    )
    async def help(self, interaction: Interaction, command: str = None):
        map = {
            "leaderboard": self.leaderboard,
            "victory": self.victory,
            "rename_game_mode": self.rename_game_mode,
            "remove_last_victory": self.remove_last_victory,
            "vc_select_random_user": self.vc_select_random_user,
            "split_vc_into_teams": self.split_vc_into_teams,
        }
        if command:
            message = map[command]
        else:
            message = "\n".join(map.values())
        embed = embed_generator(EmbedType.HELP, message)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Help(bot))
