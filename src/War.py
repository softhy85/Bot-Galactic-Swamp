import discord
from discord import Embed, app_commands
from discord.ext import commands
import os


class War(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.synced = False
        super().__init__()


    @commands.Cog.listener()
    async def on_ready(self):
        print("War cog loaded.")

    @commands.command()
    async def sync_war(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(fmt)} commands.')

    @app_commands.command(name="war", description="war")
    async def war(self, interaction=discord.Interaction):
        await interaction.response.send_message("Yes")


async def setup(bot: commands.Bot):
    await bot.add_cog(War(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])