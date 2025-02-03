from discord import Member, Interaction, NotFound, Forbidden
from discord.app_commands import rename, describe, command, autocomplete
from discord.ext.commands import Bot, Cog, has_permissions

from utils import mode_autocomplete, embed_generator, generate_leaderboard

from database import create_victory, delete_last_victory, read_updatable_messages, delete_updatable_message, Code


class Victories(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def update_message(self, interaction: Interaction):
        guild = interaction.guild
        responce = await read_updatable_messages(guild.id)
        if responce.code is not Code.SUCCESS:
            embed = embed_generator(
                "error", "Не вдалося редагувати оновлювані повідомлення.")
            await interaction.response.send_message(embed=embed)
            return
        for message in responce.data:
            message_id = message["message_id"]
            channel_id = message["channel_id"]
            channel = guild.get_channel(channel_id)
            if channel is None:
                await delete_updatable_message(guild.id, channel_id, message_id)
                embed = embed_generator("warning", f"Не вдалось оновити таблицю лідерів у каналі <#{
                                        channel_id}>. Вона не буде оновлюватись у майбутньому.")
                await interaction.channel.send(embed=embed)
                continue
            try:
                msg = await channel.fetch_message(message_id)
            except NotFound:
                await delete_updatable_message(guild.id, channel_id, message_id)
                embed = embed_generator("warning", f"Не вдалось оновити таблицю лідерів у каналі <#{
                                        channel_id}>. Вона не буде оновлюватись у майбутньому.")
                await interaction.channel.send(embed=embed)
                continue
            except Forbidden:
                embed = embed_generator("warning", f"Не вдалось оновити таблицю лідерів у каналі <#{
                                        channel_id}>. Відсутній доступ до приватного каналу.")
                await interaction.channel.send(embed=embed)
                continue
            if message["name"]:  # mode name
                embed = await generate_leaderboard(
                    interaction, message["name"])
            else:
                embed = await generate_leaderboard(interaction)
            await msg.edit(embed=embed)

    @has_permissions(administrator=True)
    @command(description="Додає перемогу гравцю")
    @rename(user="гравець", mode="режим")
    @describe(user="Гравець, якому треба додати перемогу", mode="Назва режиму гри")
    @autocomplete(mode=mode_autocomplete)
    async def victory(self, interaction: Interaction, user: Member, mode: str):
        responce = await create_victory(interaction.guild.id, user.id, mode)
        if responce.code == Code.SUCCESS:
            embed = embed_generator(
                "success", f"Додано перемогу гравцю <@{user.id}> у режимі **{mode}**.")
            await interaction.response.send_message(embed=embed)
            await self.update_message(interaction)
            # await self.bot.make_roles_names(interaction.guild)
        else:
            embed = embed_generator("error", "Щось пішло не так.")
            await interaction.response.send_message(embed=embed)

    @has_permissions(administrator=True)
    @command(description="Видаляє останню додану перемогу")
    async def remove_last_victory(self, interaction: Interaction):
        responce = await delete_last_victory(interaction.guild.id)
        if responce.code == Code.SUCCESS:
            user_id = responce.data["user_id"]
            mode_name = responce.data["name"]
            embed = embed_generator(
                "success", f"Видалено перемогу гравцю <@{user_id}> у режимі **{mode_name}**.")
        else:
            embed = embed_generator(
                "error", "Не вдалося видалити перемогу.")
        await interaction.response.send_message(embed=embed)

        await self.update_message(interaction)
        # await self.bot.make_roles_names(interaction.guild)


async def setup(bot: Bot):
    await bot.add_cog(Victories(bot))
