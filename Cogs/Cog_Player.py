import datetime
import os
import re
import time
from typing import List

import discord
from bson import ObjectId
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from pymongo.cursor import Cursor

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Colors import Colors
from Models.Emoji import Emoji
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model
from Utils.Autocomplete import Autocomplete
from Utils.Utils import Utils


class Cog_Player(commands.Cog):
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

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Player")

    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="player_infos", description="Displays player's informations")
    @app_commands.describe(pseudo="Player's username")
    @app_commands.autocomplete(pseudo=autocomplete.player_api_autocomplete)
    @app_commands.checks.has_any_role('Admin','Assistant')
    async def player_infos(self, interaction: discord.Interaction, pseudo: str):
        await interaction.response.defer()
        no_alliance = True
        player: Player_Model = self.bot.galaxyLifeAPI.get_player_infos_from_name(pseudo)
        return_player = self.bot.db.get_one_player("pseudo", "temp_player")
        return_player["temp_pseudo"] = pseudo
        self.bot.db.update_player(return_player)
        if player is None:
            await interaction.followup.send(f"> **{pseudo}** doesnt exist in the game... Did you spell it correctly ? 👀")
            return 
        player_stats: dict = self.bot.galaxyLifeAPI.get_player_stats(player["player_id_gl"])
        steam_url = self.bot.galaxyLifeAPI.get_steam_url(player["player_id_gl"])
        avatar_url = player["avatar_url"]
        title: str = f"{pseudo.upper()}" 
        if player['alliance_name'] != None and player['alliance_name'] != "":
            description: str = f"lvl **{player['player_lvl']}**\nAlliance: **{player['alliance_name']}**" 
        else:
            description: str = f"lvl **{player['player_lvl']}**\n**No alliance**"
        empty_space_colos = self.utils.empty_space("Colos:", str(len(player['colo_list'])), 17)
        empty_space_moved = self.utils.empty_space("Moved:", str(player_stats['colonies_moved']), 17)
        field: list = [f"Steam account:",
                       f"Planets:",
                       f"```🌍 Base:       lvl {player['mb_lvl']}\n🪐 Colos:{empty_space_colos}{len(player['colo_list'])}\n🔎 Moved:{empty_space_moved}{player_stats['colonies_moved']}```"]
        if player['alliance_name'] != "" and player['alliance_name'] != None:
            field.append("Alliance:")
            no_alliance = False
            alliance_check = self.utils.has_alliance(player['alliance_name'])
            alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(player['alliance_name'])
            if alliance_api_info['alliance_winrate'] != -1:
                alliance_winrate = alliance_api_info['alliance_winrate']
            else:
                alliance_winrate = "xx.xx"
            empty_space_level = self.utils.empty_space("Level:", alliance_api_info['alliance_lvl'], 18)
            empty_space_score = self.utils.empty_space("Score:", alliance_api_info['alliance_formatted_score'], 18)
            empty_space_members = self.utils.empty_space("Members:", str(len(alliance_api_info['members_list'])), 18)
            empty_space_wr = self.utils.empty_space("WR:", str(alliance_winrate), 17)
            field.append(f"```💫 Score:{empty_space_score}{alliance_api_info['alliance_formatted_score']}\n📈 WR:{empty_space_wr}{alliance_api_info['alliance_winrate'] if alliance_api_info['alliance_winrate'] != -1 else 'xx.xx'}% \n⭐ Level:{empty_space_level}{alliance_api_info['alliance_lvl']}\n👤 Members:{empty_space_members}{len(alliance_api_info['members_list'])}```")
        embed: discord.Embed = discord.Embed(title=title, description=description, color=discord.Color.from_rgb(130, 255, 128))
        embed.set_thumbnail(url=avatar_url)
        view = View()
        display: list = [embed, view]
        button_steam = Button(label = f"Steam", style=discord.ButtonStyle.blurple, emoji="🔗", url=f"{steam_url}")
        if player['alliance_name'] != "" and player['alliance_name'] != None:
            self.utils.button_alliance(player['alliance_name'], alliance_check, display)
        display[1].add_item(button_steam)
        display = self.utils.button_details(display, field, no_alliance)
        await interaction.followup.send(embed=display[0], view=display[1])     

    @app_commands.command(name="player_update", description="Update player's state")
    @app_commands.describe(pseudo="Player's username", player_state="Player's state")
    @app_commands.autocomplete(pseudo=autocomplete.player_war_autocomplete, player_state=autocomplete.player_state_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def player_update(self, interaction: discord.Interaction, pseudo: str, player_state: str):
        return_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if return_player is None:
            await interaction.response.send_message(f"> **{pseudo}** doesnt exist in the database... Did you spell it correctly ? 👀")
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
            await interaction.response.send_message(f"> Player **{pseudo}** has been set to {player_state}.")

    @app_commands.command(name="player_colonies", description="Display the infos of the Colonies of a Cog_Player")
    @app_commands.describe(pseudo="Player's username")
    @app_commands.autocomplete(pseudo=autocomplete.player_db_autocomplete)
    async def player_colonies(self, interaction: discord.Interaction, pseudo: str):
        player: Player_Model = self.bot.galaxyLifeAPI.get_player_infos_from_name(pseudo)
        if player is None:
            await interaction.response.send_message(f"> **{pseudo}** doesnt exist in the game... Did you spell it correctly ? 👀")
        else:
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies({"id_gl": int(player['player_id_gl'])}))
            if len(colonies) == 0:
                await interaction.response.send_message(f"> The colonies could not be found in the database. Add **{pseudo}** first ✨")
            else:
                embed: discord.Embed
                embed = discord.Embed(title=f"Colonies of: {pseudo}️", description=" ", color=Colors.gold, timestamp=datetime.datetime.now())
                field_number: int = 0
                for colony in colonies:
                    if colony["updated"] != False or colony["colo_coord"]["x"] > -1:
                        embed.add_field(name=f"{ Emoji.colo.value if colony['colo_status'] == 'Up' else Emoji.down.value } Colonie {colony['number']} : {colony['colo_sys_name']}",value=f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']})", inline=False)
                        field_number += 1
                if field_number != 0:
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"> Sadly, we dont have any colony for **{pseudo}**... 🫥")
                
    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Player(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])