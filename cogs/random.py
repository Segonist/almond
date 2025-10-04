import discord
from discord.app_commands import command, rename, describe, choices, Choice
from discord.ext.commands import Cog, Bot

from random import choice

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
    async def vc_random_user(
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


async def setup(bot: Bot):
    await bot.add_cog(Random(bot))
