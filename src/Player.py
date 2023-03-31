import datetime
import discord
from discord import app_commands
from discord.ext import commands
from models.War_Model import War_Model
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from pymongo.cursor import Cursor
from typing import List
import os
import re


class Player(commands.Cog):
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
        print("Cog Loaded: Player")

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        obj: dict = {}
        if current != "":
            obj = {"name": {"$regex": re.compile(current, re.IGNORECASE)}}
        alliances: List[Alliance_Model] = list(self.bot.db.get_alliances(obj))
        alliances = alliances[0:25]
        return [
            app_commands.Choice(name=alliance["name"], value=alliance["name"])
            for alliance in alliances
        ]
    async def player_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        obj: dict = {}
        if current != "":
            obj = {"pseudo": {"$regex": re.compile(current, re.IGNORECASE)}}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        players = players[0:25]
        return [
            app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
            for player in players
        ]
        
    async def player_war_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is None:
            return []
        else:
            if current == "":
                obj: dict = {"_alliance_id": act_war["_alliance_id"]}
            else:
                obj: dict = {"_alliance_id": act_war["_alliance_id"], "pseudo": {"$regex": re.compile(current, re.IGNORECASE)}}
            players: List[Player_Model] = self.bot.db.get_players(obj)
            players = players[0:25]
            return [
                app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
                for player in players
            ]
            
    async def player_state_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]: 
        data = []
        for choice in [f"🛡️ Bunker MB", "🛡️ All Bunkers", "♻️ Reset", "🕸️ AFK", "❓ Unknown" ]:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data   
      
    @app_commands.command(name="player_infos", description="Displays player's informations")
    @app_commands.describe(pseudo="Player's pseudo")
    @app_commands.checks.has_any_role('Admin','Assistant')
    async def player_add(self, interaction: discord.Interaction, pseudo: str):
        player: Player_Model = self.bot.galaxylifeapi.get_player_infos_from_name(pseudo)
        steam_url = self.bot.galaxylifeapi.get_steam_url(player["player_id_gl"])
        avatar_url = player["avatar_url"]
        title: str = f"{pseudo}" 
        if player['alliance_name'] != None:
            description: str = f"Niveau **{player['player_lvl']}**\nAlliance: **{player['alliance_name']}**" 
        else:
            description: str = f"Niveau **{player['player_lvl']}**\nSans alliance"
        field: list = [f"Planètes:", f"🌍 MB niv {player['mb_lvl']}\n:ringed_planet: Colonies: {len(player['colo_list'])}", f"Compte steam:"]
        embed: discord.Embed = discord.Embed(title=title, description=description, color=discord.Color.from_rgb(130, 255, 128))
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name=field[0],value=field[1], inline=True)
        embed.add_field(name=field[2],value=steam_url, inline=True)
        await interaction.response.send_message(embed=embed)     
   
    @app_commands.command(name="player_remove", description="Remove an existent Player")
    @app_commands.describe(pseudo="Player's pseudo")
    @app_commands.autocomplete(pseudo=player_autocomplete)
    @app_commands.checks.has_role('Admin')
    async def player_remove(self, interaction: discord.Interaction, pseudo: str):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot remove Players with a pseudo composed only of whitespace.")
            return
        return_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if return_player is None:
            await interaction.response.send_message(f"Player named {pseudo} does not exist.")
        else:
            self.bot.db.remove_player(return_player)
            await interaction.response.send_message(f"Player named {pseudo} as been removed.")
            await self.bot.dashboard.update_Dashboard()

    @app_commands.command(name="player_update", description="Update player's state")
    @app_commands.describe(pseudo="Player's pseudo", player_state="Etat du bunker")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, player_state=player_state_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def player_update(self, interaction: discord.Interaction, pseudo: str, player_state: str):
        return_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if return_player is None:
            await interaction.response.send_message(f"Player named {pseudo} does not exist.")
        else:
            if player_state == "🛡️ Bunker MB":
                return_player["state"] = "MB_full"
            elif player_state == "🛡️ All Bunkers":
                return_player["state"] = "everything_full"
            elif player_state == "🕸️ AFK":
                return_player["state"] = "afk"
            elif player_state == "❓ Unknown":
                return_player["state"] = "unknown"
            else:
                return_player["state"] = False
            self.bot.db.update_player(return_player)
            await interaction.response.send_message(f"Bunkers of {pseudo} have been updated.")
            await self.bot.dashboard.update_Dashboard()
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Player(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])