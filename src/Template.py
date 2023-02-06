import discord
from discord import Embed, app_commands
from discord.ext import commands
from models.Alliance_Model import Alliance_Model
from models.War_Model import War_Model
from typing import List
from discord.ext.commands import Context
import os


class Template(commands.Cog):
    bot: commands.Bot = None
    synced: bool = False
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.synced = False
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Template cog loaded.")

    @commands.command()
    async def sync_war(self, ctx: Context) -> None:
        if self.bot.spec_role.admin_role(ctx.guild, ctx.author):
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f'Synced {len(fmt)} commands.')
        else:
            await ctx.send("You don't have the permission to do this command.")

#    async def template_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
#        alliances = self.bot.db.get_all_alliances()
#        return [
#            app_commands.Choice(name=alliance["name"], value=alliance["name"])
#            for alliance in alliances
#        ]

    @app_commands.command(name="template", description="template")
    @app_commands.describe()
#    @app_commands.autocomplete(template=template_autocomplete)
    @app_commands.default_permissions()
    async def template(self, interaction: discord.Interaction, alliance: str, alliance_lvl: int=-1):
        print("a")

async def setup(bot: commands.Bot):
    await bot.add_cog(Template(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])