from discord.ext.commands import command, is_owner, Context, Cog, Bot

from utils import embed_generator, EmbedType


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(
        name="load",
        description="Load a cog",
    )
    @is_owner()
    async def load(self, context: Context, cog: str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception:
            embed = embed_generator(
                EmbedType.ERROR, description=f"Could not load the `{cog}` cog."
            )
            await context.send(embed=embed)
            return
        embed = embed_generator(
            EmbedType.SUCCESS, description=f"Successfully loaded the `{cog}` cog."
        )
        await context.send(embed=embed)

    @command(
        name="unload",
        description="Unloads a cog.",
    )
    @is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception:
            embed = embed_generator(
                EmbedType.ERROR, description=f"Could not unload the `{cog}` cog."
            )
            await context.send(embed=embed)
            return
        embed = embed_generator(
            EmbedType.SUCCESS, description=f"Successfully unloaded the `{cog}` cog."
        )
        await context.send(embed=embed)

    @command(
        name="reload",
        description="Reloads a cog.",
    )
    @is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except Exception as e:
            print(e)
            embed = embed_generator(
                EmbedType.ERROR, f"Could not reload the `{cog}` cog."
            )
            await context.send(embed=embed)
            return
        embed = embed_generator(
            EmbedType.SUCCESS, f"Successfully reloaded the `{cog}` cog."
        )
        await context.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))
