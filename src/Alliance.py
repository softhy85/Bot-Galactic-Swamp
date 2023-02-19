import discord
from discord import app_commands
from discord.ext import commands
from models.Alliance_Model import Alliance_Model
from typing import List
import os


class Alliance(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Alliance cog loaded.")

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        alliances: List[Alliance_Model] = list(self.bot.db.get_alliances({"name": {"$regex": current}}))
        alliances = alliances[0:25]
        return [
            app_commands.Choice(name=alliance["name"], value=alliance["name"])
            for alliance in alliances
        ]

    @app_commands.command(name="alliance_add", description="Add a new Alliance to the db")
    @app_commands.describe(alliance="Alliance's name", alliance_lvl="Alliance's level")
    @app_commands.checks.has_role('Admin')
    async def alliance_add(self, interaction: discord.Interaction, alliance: str, alliance_lvl: int=-1):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot create Alliances with a name composed only of whitespace.")
            return
        return_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if return_alliance is None:
            new_alliance: Alliance_Model = {"name": alliance, "alliance_lvl": alliance_lvl}
            new_alliance["_id"] = self.bot.db.push_new_alliance(new_alliance)
            if new_alliance["_id"] is None:
                await interaction.response.send_message(f"Something goes wrong while creating the Alliance {alliance}.\nPlease report this bug to Softy.")
                return
            await interaction.response.send_message(f"Alliance named {alliance} created.")
        else:
            await interaction.response.send_message(f"Alliance named {alliance} already exist.")

    @app_commands.command(name="alliance_update", description="Update an existent Alliance")
    @app_commands.describe(alliance="Alliance's name", alliance_lvl="Alliance's level")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    async def alliance_update(self, interaction: discord.Interaction, alliance: str, alliance_lvl: int):
        return_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot update Alliances with a name composed only of whitespace.")
            return
        if return_alliance is None:
            await interaction.response.send_message(f"Alliance named {alliance} does not exist.")
        else:
            return_alliance["alliance_lvl"] = alliance_lvl
            self.bot.db.update_alliance(return_alliance)
            await interaction.response.send_message(f"Alliance named {alliance} updated.")

    @app_commands.command(name="alliance_remove", description="Remove an existent Alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    async def alliance_remove(self, interaction: discord.Interaction, alliance: str):
        return_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot remove Alliances with a name composed only of whitespace.")
            return
        if return_alliance is None:
            await interaction.response.send_message(f"Alliance named {alliance} does not exist.")
        else:
            self.bot.db.remove_alliance(return_alliance)
            await interaction.response.send_message(f"Alliance named {alliance} as been removed.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Alliance(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])