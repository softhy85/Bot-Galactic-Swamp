import os
from typing import List

import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.ui import Button, Select, View

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Emoji import Emoji
from Models.Player_Model import Player_Model


class Cog_Misc(commands.Cog):
    bot: commands.bot = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Misc")                

    @app_commands.command(name="db", description="How many colonies have been scouted yet")
    async def db(self, interaction: discord.Interaction):
        colo_number: List[Colony_Model] = list(self.bot.db.get_all_updated_colonies())
        colo_found_number: List[Colony_Model] = list(self.bot.db.get_all_found_colonies())
        embed = discord.Embed(title=f">>> **{len(colo_number)}** 🪐 colonies from enemy alliances have been updated yet.\n**{len(colo_found_number)}** 🪐 colonies found by screening \n**{len(colo_number)+len(colo_found_number)}** 🪐 colonies in total")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="team", description="Spy your mates because they don't answer you")
    @app_commands.checks.has_any_role('Admin','Assistant')
    async def team(self, interaction: discord.Interaction): 
        await interaction.response.defer()
        embed: discord.Embed = discord.Embed(title=f"<:empty:1088454928474841108>Crew Overview", description="Use the bot or you will be \n*smashed* 🔨 by Diablo.", color=discord.Color.from_rgb(255, 100, 100))
        obj: dict = {"name", "GALACTIC SWAMP"}
        alliance: Alliance_Model = self.bot.db.get_one_alliance("name", "GALACTIC SWAMP")
        obj: dict = {"_alliance_id": alliance['_id']}
        alliance_players: List[Player_Model] = list(self.bot.db.get_players(obj))
        value = ">>> "
        alliance_players.sort(key=lambda item: item.get("lvl"), reverse=True)
        it = 0
        for player in alliance_players:
            status = self.bot.galaxyLifeAPI.get_player_status(player["id_gl"])
            if status == None:
                status = 0
            alliance_players[it]["status_steam"] = status
            it += 1
        alliance_players.sort(key=lambda item: item.get("status_steam"), reverse=True)
        for player in alliance_players:    
            if player["status_steam"] == 0:
                emoji = Emoji.offline.value
            elif player["status_steam"] == 1:
                emoji = Emoji.maybe.value
            else:
                emoji = Emoji.online.value
            value = value + emoji + " " + player["pseudo"] + "\n"
        embed.add_field(name="Members:",value=value, inline=False)
        # embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        view = View()
        await interaction.followup.send(embed=embed, view=view)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Misc(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])