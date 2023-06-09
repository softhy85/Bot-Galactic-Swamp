import os
import re
import time
from typing import List

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Colors import Colors
from Models.Emoji import Emoji
from Models.Player_Model import Player_Model
from Utils.Autocomplete import Autocomplete
from Utils.Utils import Utils


class Cog_Alliance(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    autocomplete = Autocomplete
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.utils = Utils(bot)
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.command_channel_id: int = int(os.getenv("COMMAND_CHANNEL"))
        self.command_channel = self.bot.get_channel(self.command_channel_id)
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Alliance")

    #</editor-fold>

    #<editor-fold desc="command">
       
    @app_commands.command(name="alliance_colonies", description="Get all colonies from an alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=autocomplete.alliance_autocomplete)
    @app_commands.checks.has_any_role('Admin','Assistant')
    async def alliance_colonies(self, interaction: discord.Interaction,  alliance: str): 
        await interaction.response.defer()
        alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
        if alliance_info == None:
            await interaction.followup.send(f"> The alliance called **{alliance}** doesnt exist in the database... Did you spell it correctly ? 👀")
        alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(alliance_info["name"])
        colo_found_number: List[Colony_Model] = list(self.bot.db.get_all_found_colonies())
        obj: dict = {"_alliance_id": alliance_info["_id"]}
        players: List[Player_Model] = self.bot.db.get_players(obj)
        embed: discord.Embed = discord.Embed(title=f"{alliance_info['name']}", description="", color=discord.Color.from_rgb(8, 1, 31))
        embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        total_size: int = 0
        field_count: int = 0
        colo_count: int = 0
        answer: str = ""
        for player in players:
            value: str = ""
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            for colo in colonies:
                if colo['colo_sys_name'] != "-1":
                    colo_sys_name: str = colo['colo_sys_name']
                else:
                    colo_sys_name: str = "Unknown System"
                if colo['colo_coord']['x'] != -1:
                    value = value + f"\n🪐 n° **{colo['number']}**  - SB {colo['colo_lvl']}:\n `{colo_sys_name} ({colo['colo_coord']['x']} :{colo['colo_coord']['y']})` \n"
                    colo_count += 1
            if value != "": 
                embed.add_field(name=f"\n✅ {player['pseudo']}", value=value, inline=False)
                field_count += 1
            total_size += len(value) + len(player) + 5
            for it in range(len(colo_found_number)):
                if int(colo_found_number[it]["gl_id"]) == int(player["id_gl"]):
                    answer = answer + f"> ✅ **{player['pseudo']}** : \n🪐 `({colo_found_number[it]['X']} ; {colo_found_number[it]['Y']})`\n"
            if total_size >= 2500 or field_count >= 20:
                await interaction.followup.send(embed=embed)
                embed: discord.Embed = discord.Embed(title="", description="", color=discord.Color.from_rgb(8, 1, 31)) 
                total_size: int = 0
                field_count: int = 0
        if answer != "":
            embed.add_field(name='Other colonies', value="*(might be imprecise)*")
            embed.add_field(name=' ', value=answer, inline=False)
        embed.description = f"({colo_count} colonies)"
        if total_size != 0:
            await interaction.followup.send(embed=embed)

    
    @app_commands.command(name="alliance_infos", description="Informations and stats about an alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=autocomplete.alliance_autocomplete)
    async def alliance_infos(self, interaction: discord.Interaction,  alliance: str): 
        alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(alliance)
        if not alliance_api_info:
            await interaction.response.send_message(f"> The alliance called **{alliance}** doesnt exist in the game... Did you spell it correctly ? 👀")
            return 
        if alliance_api_info['alliance_winrate'] != -1:
            alliance_winrate = alliance_api_info['alliance_winrate']
        else:
            alliance_winrate = "xx.xx"
        empty_space_level = self.utils.empty_space("Level:", alliance_api_info['alliance_lvl'], 18)
        empty_space_score = self.utils.empty_space("Score:", alliance_api_info['alliance_formatted_score'], 18)
        empty_space_members = self.utils.empty_space("Members:", str(len(alliance_api_info['members_list'])), 18)
        empty_space_wr = self.utils.empty_space("WR:", str(alliance_winrate), 17)
        description = f"```💫 Score:{empty_space_score}{alliance_api_info['alliance_formatted_score']}\n📈 WR:{empty_space_wr}{alliance_api_info['alliance_winrate'] if alliance_api_info['alliance_winrate'] != -1 else 'xx.xx'}% \n⭐ Level:{empty_space_level}{alliance_api_info['alliance_lvl']}\n👤 Members:{empty_space_members}{len(alliance_api_info['members_list'])}```"
        alliance_check = self.utils.has_alliance(alliance)
        embed: discord.Embed = discord.Embed(title=f"{alliance.upper()}", description=description, color=discord.Color.from_rgb(130, 255, 128))
        embed.add_field(name=f"",value=alliance_api_info['alliance_description'], inline=False)
        embed.set_thumbnail(url=alliance_api_info["emblem_url"])
        view = View()
        display: list = [embed, view]
        self.utils.button_alliance(alliance, alliance_check, display)
        await interaction.response.send_message(embed=display[0], view=display[1])      
        
    @app_commands.command(name="alliance_leaderboard", description="Leaderboard")
    async def alliance_leaderboard(self, interaction: discord.Interaction): 
        leaderboard: dict = self.bot.galaxyLifeAPI.get_alliance_leaderboard()
        embed =discord.Embed(title=f"️Leaderboard", description="", color=Colors.dark_magenta)
        name: str = f"📈 Current Rank: "
        value: str = (f"```ansi\n\u001b[0;0m{leaderboard['3']-2}# ⏫ {leaderboard['-2']['Name']}:    +\u001b[0;31m{leaderboard['-2']['Warpoints']-leaderboard['0']['Warpoints']}\u001b[0;0m"+
                      f"\n{leaderboard['3']-1}# 🔼 {leaderboard['-1']['Name']}:    +\u001b[0;31m{leaderboard['-1']['Warpoints']-leaderboard['0']['Warpoints']}\u001b[0;0m"+
                      f"\n{leaderboard['3']}# ✅ {leaderboard['0']['Name']}:    {leaderboard['0']['Warpoints']}"+
                      f"\n{leaderboard['3']+1}# 🔽 {leaderboard['1']['Name']}:    -\u001b[0;30m{abs(leaderboard['1']['Warpoints']-leaderboard['0']['Warpoints'])}\u001b[0;0m"+
                      f"\n{leaderboard['3']+2}# ⏬ {leaderboard['2']['Name']}:    -\u001b[0;30m{abs(leaderboard['2']['Warpoints']-leaderboard['0']['Warpoints'])}\u001b[0;0m```")
        embed.add_field(name=name, value=value, inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/943168885333581886/a_12f99da94b70ba0624195d65327f33ce.gif")
        await interaction.response.send_message(embed=embed)
        
    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Alliance(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])