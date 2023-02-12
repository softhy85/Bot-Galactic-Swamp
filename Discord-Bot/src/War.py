import discord
from discord import Embed, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from models.Alliance_Model import Alliance_Model
from models.War_Model import War_Model, Status
from typing import List
import os


class War(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    general_channel_id: int = None
    general_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id: int = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.war_channel_id)
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print("War cog loaded.")

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        alliances = self.bot.db.get_all_alliances()
        return [
            app_commands.Choice(name=alliance["name"], value=alliance["name"])
            for alliance in alliances
        ]

    @app_commands.command(name="war_new", description="Start a new war")
    @app_commands.describe(alliance="The name of the alliance against which you are at war", alliance_lvl="The level of the alliance")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.default_permissions()
    async def war_new(self, interaction: discord.Interaction, alliance: str, alliance_lvl: int=-1):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot create Alliances with a name composed only of whitespace.")
            return
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            await interaction.response.send_message(f"We are already at war with {actual_war['alliance_name']}.")
            return
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if war_alliance is None:
            new_alliance: Alliance_Model = {"name": alliance, "alliance_lvl": alliance_lvl}
            new_alliance["_id"] = self.bot.db.push_new_alliance(new_alliance)
            if new_alliance["_id"] is None:
                await interaction.response.send_message(f"Something goes wrong while creating the Alliance {alliance}.\nPlease report this bug to Softy.")
                return
            await interaction.response.send_message(f"Alliance named {alliance} created.")
            war_alliance = new_alliance
        new_message: discord.Message = await self.war_channel.send(f"@everyone nous sommes en guerre contre {war_alliance['name']}")
#        new_message: discord.Message = await self.war_channel.send(f"nous sommes en guerre contre {war_alliance['name']}")
        new_thread: discord.Thread = await new_message.create_thread(name=war_alliance["name"])
        new_war: War_Model = {"_alliance_id": war_alliance["_id"], "alliance_name": war_alliance["name"], "id_thread": new_thread.id, "enemy_point": 0, "point": 0, "status": "InProgress"}

        new_war["_id"] = self.bot.db.push_new_war(new_war)
        await interaction.response.send_message("New wars created.")
        await self.bot.dashboard.create_Dashboard(new_war)

    @app_commands.command(name="war_update", description="Update the actual war")
    @app_commands.describe(status="Status",point="The point of our alliance", enemy_point="The point of the enemy alliance")
    @app_commands.default_permissions()
    async def war_update(self, interaction: discord.Interaction, status: Status = Status.InProgress, point: int=-1, enemy_point: int=-1):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if status.value == 1 and point == -1 and enemy_point == -1:
            await interaction.response.send_message("No modification will be done.")
            return
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is None:
            await interaction.response.send_message("No war actually in progress.")
        else:
            actual_war["status"] = status.name
            if point != -1:
                actual_war["point"] = point
            if enemy_point != -1:
                actual_war["enemy_point"] = enemy_point
            self.bot.db.update_war(actual_war)
            await interaction.response.send_message(f"The actual war again {actual_war['alliance_name']} as been updated.")
            if status.value != 1:
                war_thread: discord.Thread = interaction.guild.get_thread(actual_war['id_thread'])
                if status.value == 2:
                    if war_thread is not None:
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Win",archived=True, locked=True)
                    await self.general_channel.send(f"The actual war again {actual_war['alliance_name']} is won.")
                if status.value == 3:
                    if war_thread is not None:
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Lost",archived=True, locked=True)
                    await self.general_channel.send(f"The actual war again {actual_war['alliance_name']} is lost.")
                if status.value == 4:
                    if war_thread is not None:
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Ended",archived=True, locked=True)
                    await self.general_channel.send(f"The actual war again {actual_war['alliance_name']} has ended.")

async def setup(bot: commands.Bot):
    await bot.add_cog(War(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])