import discord
from discord import app_commands
from discord.ext import commands
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.Colors import Colors
from typing import List
import os
import re


class Cog_Alliance(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.backup_channel_id: int = int(os.getenv("COLO_BACKUP_CHANNEL"))
        self.backup_channel = self.bot.get_channel(self.backup_channel_id)
        self.command_channel_id: int = int(os.getenv("COMMAND_CHANNEL"))
        self.command_channel = self.bot.get_channel(self.command_channel_id)

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Alliance")

    #</editor-fold>

    #<editor-fold desc="autocomplete">

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        obj: dict = {}
        if current != "":
            obj: dict = {"name": {"$regex": re.compile(current, re.IGNORECASE)}}
        alliances: List[Alliance_Model] = list(self.bot.db.get_alliances(obj))
        alliances = alliances[0:25]
        return [
            app_commands.Choice(name=alliance["name"], value=alliance["name"])
            for alliance in alliances
        ]

    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="alliance_add", description="Add a new Cog_Alliance to the db")
    @app_commands.describe(alliance="The name of the alliance")
    @app_commands.checks.has_role('Admin')
    @app_commands.default_permissions()
    async def alliance_add(self, interaction: discord.Interaction, alliance: str):
        await interaction.response.defer(ephemeral=True)
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.followup.send("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.followup.send(f"Cannot create alliances with a name composed only of whitespace.")
            return
        act_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
        if act_alliance is None:
            await interaction.followup.send("> Loading the new alliance.")
        else:
            await interaction.followup.send("> Updating the alliance.")
        await self.bot.alliance.update_alliance(alliance)

    @app_commands.command(name="alliance_update", description="Update an existent Cog_Alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    async def alliance_update(self, interaction: discord.Interaction, alliance: str, alliance_lvl: int):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot update Alliances with a name composed only of whitespace.")
            return
        return_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if return_alliance is None:
            await interaction.response.send_message(f"Alliance named {alliance} does not exist.")
        else:
            return_alliance["alliance_lvl"] = alliance_lvl
            self.bot.db.update_alliance(return_alliance)
            await interaction.response.send_message(f"Alliance named {alliance} updated.")

    @app_commands.command(name="alliance_remove", description="Remove an existent Cog_Alliance")
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
       
    @app_commands.command(name="alliance_colonies", description="Get all colonies from an alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_any_role('Admin')
    async def alliance_colonies(self, interaction: discord.Interaction,  alliance: str): 
        alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(alliance_info["name"])
        obj: dict = {"_alliance_id": alliance_info["_id"]}
        players: List[Player_Model] = self.bot.db.get_players(obj)
        await interaction.response.send_message(f"Here's the database for {alliance_info['name']}:")
        embed: discord.Embed = discord.Embed(title=f"➖➖➖➖ {alliance_info['name']} ➖➖➖➖", description=" \n ", color=discord.Color.from_rgb(8, 1, 31))
        embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        total_size: int = 0
        field_count: int = 0
        for player in players:
            value: str = ""
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colo in colonies:
                if colo['colo_coord']['x'] != -1:
                    value = value + f"\n🪐 **__(SB{colo['colo_lvl']}):__**\n/colo_update pseudo:{player['pseudo']} colo_number:{colo['number']} colo_sys_name:{colo['colo_sys_name']} colo_coord_x:{colo['colo_coord']['x']} colo_coord_y:{colo['colo_coord']['y']}\n"
            if value != "": 
                embed.add_field(name=f"\n✅ {player['pseudo']}",value=value, inline=False)
                field_count += 1
        
            total_size += len(value) + len(player) + 5
            if total_size >= 2500 or field_count >= 20:
                await self.backup_channel.send(embed=embed)
                embed: discord.Embed = discord.Embed(title="", description="", color=discord.Color.from_rgb(8, 1, 31)) 
                total_size: int = 0
                field_count: int = 0
        if total_size != 0:
            await self.backup_channel.send(embed=embed)

    # @app_commands.command(name="alliance_colonies", description="Get all colonies from an alliance")
    # @app_commands.describe(alliance="Alliance's name")
    # @app_commands.autocomplete(alliance=alliance_autocomplete)
    # @app_commands.checks.has_any_role('Admin')
    # async def alliance_infos(self, interaction: discord.Interaction,  alliance: str): 
    #     alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
    #     alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(alliance_info["name"])
    #     obj: dict = {"_alliance_id": alliance_info["_id"]}
    #     players: List[Player_Model] = self.bot.db.get_players(obj)
    #     print(alliance_api_info["alliance_score"])
    #     await interaction.response.send_message(f"Here's the database for {alliance_api_info['alliance_score']}:")
    #     embed: discord.Embed = discord.Embed(title=f"➖➖➖➖ {alliance_info['name']} ➖➖➖➖", description=f"Score: {alliance_api_info['alliance_score']} \nWinrate:{alliance_api_info['alliance_lvl']}\nLevel:{alliance_api_info['alliance_winrate']}", color=discord.Color.from_rgb(8, 1, 31))
    #     embed.set_thumbnail(url=alliance_api_info["emblem_url"])

        
    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Alliance(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])