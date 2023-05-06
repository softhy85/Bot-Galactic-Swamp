import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from Models.War_Model import War_Model
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from pymongo.cursor import Cursor
from typing import List
import os
import re
import time
from bson import ObjectId


class Cog_Player(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Player")

    #</editor-fold>

    #<editor-fold desc="autocomplete">
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
        return_player = self.bot.db.get_one_player("pseudo", "temp_player")
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
            
    async def player_api_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        if len(current) >= 4:
            players = self.bot.galaxyLifeAPI.search_for_player(current)
            if players:
                return [
                    app_commands.Choice(name=players[it]["Name"], value=players[it]["Name"])
                    for it in range(0, len(players))
                ]
            else:
                return []
        else: 
            return []
        
        
    async def player_state_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]: 
        data = []
        for choice in [f"🛡️ Bunker MB", "🛡️ All Bunkers", "♻️ Reset", "🕸️ AFK", "❓ Unknown" ]:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data

    def has_alliance(self, alliance: str):
        return_value: dict = {}
        alliance_state: list = ["Add","Adding"]
        button_style = discord.ButtonStyle.green
        alliance_db: dict = self.bot.db.get_one_alliance("name", alliance.upper())
        if alliance_db is not None:
            button_style = discord.ButtonStyle.blurple
            alliance_state: list = ["Update", "Updating"]
        return_value['alliance_state'] = alliance_state
        return_value['button_style'] = button_style
        return return_value
    
    #cog boutons?
    def button_details(self, display, field: list, no_alliance):
        button_details = Button(label = f"+", style=discord.ButtonStyle.blurple)      
        async def button_callback_more(interaction):
            button_details_2 = Button(label = f"-", style=discord.ButtonStyle.gray,  custom_id= "less")
            if no_alliance == True:
                display[1].remove_item(display[1].children[1])
            else:
                display[1].remove_item(display[1].children[2])
            display[1].add_item(button_details_2)
            display[0].add_field(name=field[1],value=field[2], inline=False)
            if no_alliance == False:
                display[0].add_field(name=field[3], value=field[4], inline=False)
            button_details_2.callback = button_callback_less
            await interaction.response.edit_message(embed=display[0], view=display[1])
        
        async def button_callback_less(interaction):
            button_details = Button(label = f"+", style=discord.ButtonStyle.blurple,  custom_id= "less")
            if no_alliance == True:
                display[1].remove_item(display[1].children[1])
            else:
                display[1].remove_item(display[1].children[2])
            display[1].add_item(button_details)
            display[0].clear_fields()
            button_details.callback = button_callback_more
            await interaction.response.edit_message(embed=display[0], view=display[1])
        button_details.callback = button_callback_more       
        display[1].add_item(button_details)
        return display
    
    # en double: cog?     
    def button_alliance(self, alliance, alliance_check: list, display):
        if alliance != None and alliance != "":
            button = Button(label = f"{alliance_check['alliance_state'][0]} Alliance", style=alliance_check['button_style'], emoji="🔒")       
            async def button_callback_alliance(interaction):
                button = Button(label = f"{alliance_check['alliance_state'][0]} Alliance ", style=discord.ButtonStyle.gray)
                display[1].clear_items()
                display[1].add_item(button)
                await interaction.response.edit_message(embed=display[0], view=display[1])
                if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
                    await interaction.followup.send("You don't have the permission to use this command.")
                    return
                act_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
                loading_message = await interaction.followup.send(f"> Loading the alliance... (started <t:{int(time.time())}:R>)")
                await self.bot.alliance.update_alliance(alliance.upper())
                await loading_message.edit(content="> Alliance Loaded ✅")
            button.callback = button_callback_alliance
            display[1].add_item(button)
        return display

    # optimisable?
    def empty_space(self, left_word, right_word, width):
        it = 0
        empty_space = ""
        empty_space_length = width - len(right_word) - len(left_word)
        while it < empty_space_length:
            empty_space = empty_space + " "
            it += 1
        return empty_space
       
    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="player_infos", description="Displays player's informations")
    @app_commands.describe(pseudo="Player's pseudo")
    @app_commands.autocomplete(pseudo=player_api_autocomplete)
    @app_commands.checks.has_any_role('Admin','Assistant')
    async def player_add(self, interaction: discord.Interaction, pseudo: str):
        no_alliance = True
        player: Player_Model = self.bot.galaxyLifeAPI.get_player_infos_from_name(pseudo)
        return_player = self.bot.db.get_one_player("pseudo", "temp_player")
        return_player["temp_pseudo"] = pseudo
        act_player = self.bot.db.update_player(return_player)
        if player is None:
            await interaction.response.send_message(f"**{pseudo}** doesn't exist as a player.")
            return 
        player_stats: dict = self.bot.galaxyLifeAPI.get_player_stats(player["player_id_gl"])
        steam_url = self.bot.galaxyLifeAPI.get_steam_url(player["player_id_gl"])
        avatar_url = player["avatar_url"]
        title: str = f"{pseudo.upper()}" 
        if player['alliance_name'] != None and player['alliance_name'] != "":
            description: str = f"lvl **{player['player_lvl']}**\nAlliance: **{player['alliance_name']}**" 
        else:
            description: str = f"lvl **{player['player_lvl']}**\n**No alliance**"
        empty_space_colos = self.empty_space("Colos:", str(len(player['colo_list'])), 17)
        empty_space_moved = self.empty_space("Moved:", str(player_stats['colonies_moved']), 17)
        field: list = [f"Steam account:",
                       f"Planets:",
                       f"```🌍 Base:       lvl {player['mb_lvl']}\n🪐 Colos:{empty_space_colos}{len(player['colo_list'])}\n🔎 Moved:{empty_space_moved}{player_stats['colonies_moved']}```"]
        if player['alliance_name'] != "" and player['alliance_name'] != None:
            no_alliance = False
            alliance_check = self.has_alliance(player['alliance_name'])
            alliance_api_info = self.bot.galaxyLifeAPI.get_alliance(player['alliance_name'])
            empty_space_score = self.empty_space("Score:", str(alliance_api_info['alliance_formatted_score']), 17)
            empty_space_level = self.empty_space("Level:", str(alliance_api_info['alliance_lvl']), 17)
            field.append("Alliance:")
            field.append(f"```💫 Score:{empty_space_score}{alliance_api_info['alliance_formatted_score']}\n📈 WR:        {alliance_api_info['alliance_winrate'] if alliance_api_info['alliance_winrate'] != -1 else 'xx.xx'}% \n⭐ Level:{empty_space_level}{alliance_api_info['alliance_lvl']}\n👤 Members:       {len(alliance_api_info['members_list'])}```")
        embed: discord.Embed = discord.Embed(title=title, description=description, color=discord.Color.from_rgb(130, 255, 128))
        embed.set_thumbnail(url=avatar_url)
        view = View()
        display: list = [embed, view]
        button_steam = Button(label = f"Steam", style=discord.ButtonStyle.blurple, emoji="🔗", url=f"{steam_url}")
        if player['alliance_name'] != "" and player['alliance_name'] != None:
            self.button_alliance(player['alliance_name'], alliance_check, display)
        display[1].add_item(button_steam)
        display = self.button_details(display, field, no_alliance)
        await interaction.response.send_message(embed=display[0], view=display[1])     

    @app_commands.command(name="player_remove", description="Remove an existent Cog_Player")
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
            await interaction.response.send_message(f"Player {pseudo} has been updated.")
            await self.bot.dashboard.update_Dashboard()

    #</editor-fold>


async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Player(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])