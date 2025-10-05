import discord
from discord.app_commands import command, rename, describe, choices, Choice
from discord.ext.commands import Cog, Bot

from random import choice, shuffle

from utils import embed_generator, EmbedType


class Random(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @rename(author_counts="автор")
    @describe(
        author_counts="(опціональний) Чи особа, що викликає команду, має бути врахована (за замовчеванням - ні)"
    )
    @command(description="Вибирає випадкову особу з голосового чату")
    @choices(
        author_counts=[
            Choice(name="так", value=1),
            Choice(name="ні", value=2),
        ]
    )
    async def vc_select_random_user(
        self, interaction: discord.Interaction, author_counts: Choice[int] = 0
    ):
        voice_state = interaction.user.voice
        if voice_state is not None:
            channel = voice_state.channel
            members = channel.members
            if not author_counts:
                members.remove(interaction.user)
            users_number = len(members)
            if users_number > 0:
                user = choice(members)
                embed = embed_generator(
                    EmbedType.RANDOM,
                    description=f"Випадкова особа - <@{user.id}>.",
                    title=f"Кидаю {users_number}-гранну кістку",
                )
            else:
                embed = embed_generator(
                    EmbedType.ERROR,
                    "В голосовому чаті недостатньо учасників.",
                )
        else:
            embed = embed_generator(
                EmbedType.ERROR, "Увійдіть до голосового чату, щоб використати команду."
            )

        await interaction.response.send_message(embed=embed)

    @rename(author_counts="автор", team_count="команди")
    @describe(
        author_counts="(опціональний) Чи особа, що викликає команду, має бути врахована (за замовчеванням - ні)",
        team_count="Кількість команд",
    )
    @command(description="Поділяє осіб у голосовому чаті на команди")
    @choices(
        author_counts=[
            Choice(name="так", value=1),
            Choice(name="ні", value=2),
        ]
    )
    async def split_vc_into_teams(
        self,
        interaction: discord.Interaction,
        team_count: int,
        author_counts: Choice[int] = 0,
    ):
        # TODO: move to another function to remove redundancy
        voice_state = interaction.user.voice
        if voice_state is not None:
            channel = voice_state.channel
            members = channel.members
            if not author_counts:
                members.remove(interaction.user)
            users_number = len(members)
            if users_number > 0:
                shuffle(members)
                teams = []
                team_size = users_number // team_count
                reminder = users_number % team_count

                for i in range(team_count):
                    teams.append(members[i * team_size : (i + 1) * team_size])
                for i in range(reminder):
                    teams[i].append(members[-(i + 1)])

                result = "Команди:"
                for i, team in enumerate(teams):
                    members_list = [f"<@{member.id}>" for member in team]
                    members = ", ".join(members_list)
                    result += f"\n{i + 1}. {members}"

                embed = embed_generator(
                    EmbedType.RANDOM,
                    description=result,
                    title=f"Кидаю {team_count}-гранну кістку",
                )
            else:
                embed = embed_generator(
                    EmbedType.ERROR,
                    "В голосовому чаті недостатньо учасників.",
                )
        else:
            embed = embed_generator(
                EmbedType.ERROR, "Увійдіть до голосового чату, щоб використати команду."
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Random(bot))
