import datetime
import os
import re
from typing import List

import discord
from discord import Embed, File, app_commands, ui
from discord.ext import commands, tasks
from discord.ui import Button, Select, View

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Colors import Colors
from Models.Emoji import Emoji
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model
from Utils.GalaxyCanvas import GalaxyCanvas


class Cog_Colony(commands.Cog):
    guild: discord.Guild = None
    bot: commands.bot = None
    experiment_channel_id: int = 0
    experiment_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    war_channel_id: int = 0
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    general_channel_id: int = 0
    general_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.experiment_channel_id = int(os.getenv("EXPERIMENT_CHANNEL"))
        self.experiment_channel = self.bot.get_channel(self.experiment_channel_id)
        self.war_channel_id  = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.war_channel_id)
        self.guild = self.bot.get_guild(int(os.getenv("SERVER_ID")))
        self.log_channel_id: int = int(os.getenv("LOG_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)


    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Colony")


    #</editor-fold>

    #<editor-fold desc="autocomplete">

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
            
    async def colo_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        pseudo = interaction.namespace.pseudo
        player: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile("^" + pseudo + "$", re.IGNORECASE)}) 
        obj: dict = {"id_gl": int(player['id_gl'])} 
        colos: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        colos.sort(key=lambda item: item.get("number"))
        colos = colos[0:25]
        return [
            app_commands.Choice(name=f'{Emoji.updated.value if colo["updated"] else Emoji.native.value} Colo n°{colo["number"]} (SB{colo["colo_lvl"]}) {colo["colo_sys_name"] if colo["updated"] else ""} {colo["colo_coord"]["x"] if colo["updated"] else ""} {colo["colo_coord"]["y"] if colo["updated"] else ""}', value=colo["number"])
            for colo in colos
        ]
            
    async def player_war_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        return_player = self.bot.db.get_one_player("pseudo", "temp_player")
        temp_pseudo: list = [{"Name":"None"}]
        temp_pseudo[0]["Name"] = return_player["temp_pseudo"]
        if act_war is None:
            if len(current) >= 4:
                players = self.bot.galaxyLifeAPI.search_for_player(current)
                if players:
                    players = players + temp_pseudo
                    return [
                        app_commands.Choice(name=players[it]["Name"], value=players[it]["Name"])
                        for it in range(0, len(players))
                    ]
            else: 
                return [
                    app_commands.Choice(name=return_player["temp_pseudo"], value=return_player["temp_pseudo"])
                ]
        else:
            if current == "":
                obj: dict = {"_alliance_id": act_war["_alliance_id"]}
            else:
                obj: dict = {"_alliance_id": act_war["_alliance_id"], "pseudo": {"$regex": re.compile(current, re.IGNORECASE)}}
            players: List[Player_Model] = list(self.bot.db.get_players(obj))
            players = players[0:25]
            temp_pseudo[0]["pseudo"] = return_player["temp_pseudo"]
            players = players + list(temp_pseudo)
            return [
                app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
                for player in players
            ]

    async def gift_state_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]: 
        data = []
        for choice in ["Always Free","Free Once", "Not Free"]:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data

    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="colo_update", description="Update a saved colony")
    @app_commands.describe(pseudo="Player's username", colo_number="if not found : ✅ run /player_infos and add its alliance ", colo_sys_name="Colony's system name (in CAPS)", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colo_update(self, interaction: discord.Interaction, pseudo: str, colo_number: int, colo_sys_name: str = "", colo_coord_x: int = -1, colo_coord_y: int = -1):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("> 🚫 You don't have the permission to use this command.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile("^" + pseudo + "$", re.IGNORECASE)})
        if act_player is None:
            await interaction.response.send_message(f"> **{pseudo}** doesnt exist in the database... Did you spell it correctly ? 👀")
        else:
            act_colony: List[Colony_Model] = list(self.bot.db.get_colonies({"id_gl": int(act_player['id_gl']), "number": colo_number}))
            if len(act_colony) == 0:
                await interaction.response.send_message(f"> The colonies could not be found in the database. Add **{pseudo}** first ✨")
            else:
                act_colony = act_colony[0]
                act_colony["colo_sys_name"] = colo_sys_name.upper()
                act_colony["colo_coord"]["x"] = colo_coord_x
                act_colony["colo_coord"]["y"] = colo_coord_y
                if colo_coord_y != -1 and colo_coord_x != -1 and act_colony["colo_sys_name"] != "-1": 
                    act_colony["updated"] = True
                else:
                    act_colony["updated"] = False
                act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
                if act_war is not None:
                    act_colony["scouted"] = True
                if act_colony["colo_sys_name"] != "-1" and act_colony["colo_coord"]["y"] != -1:
                    await interaction.response.send_message(f"> Colony n°**{colo_number}** of **{pseudo}** updated. ✅")
                    self.bot.db.update_colony(act_colony)
                elif act_colony["colo_sys_name"] != "-1" and act_colony["colo_coord"]["y"] == -1:
                    await interaction.response.send_message(f"> Colony n°**{colo_number}** of **{pseudo}** won't be updated. 🚫 (Missing the Y coordinates)")
                elif act_colony["colo_sys_name"] != "-1" and act_colony["colo_coord"]["x"] == -1:
                    await interaction.response.send_message(f"> Colony n°**{colo_number}** of **{pseudo}** won't be updated. 🚫 (Missing the X coordinates)")
                else:
                    await interaction.response.send_message(f"> Colony n°**{colo_number}** of **{pseudo}** has been removed from the updated colonies 💢")
                    self.bot.db.update_colony(act_colony)
 
    @app_commands.command(name="colo_gift", description="Gift colony to low level players / Or tell if a colony never has defenses")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="Wich colony", gift_state="x")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete,  gift_state=gift_state_autocomplete)
    async def colo_gift(self, interaction: discord.Interaction, pseudo: str,colo_number: int, gift_state: str):
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
        act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        if act_player is None:
            await interaction.response.send_message(f"> **{pseudo}** doesnt exist in the database... Did you spell it correctly ? 👀")
        else:
            act_colony = act_colony[0]
            act_colony["gift_state"]: str = gift_state
            self.bot.db.update_colony(act_colony)
            await self.log_channel.send(f"> <@&1089184438442786896> a new free colony has been added !! 🎁")
            await interaction.response.send_message(f"> The free state of colony n°{act_colony['number']} of {pseudo} has been updated. 🎁")
            
    @app_commands.command(name="colo_found_alliance", description="Find possible colonies in foundcolonies")
    @app_commands.describe(alliance="alliance name")
    async def colos_scouted(self, interaction: discord.Interaction, alliance: str):
        await interaction.response.defer()
        colo_found_number: List[Colony_Model] = list(self.bot.db.get_all_found_colonies())
        allianceDetails = self.bot.galaxyLifeAPI.get_alliance(alliance)
        for it_alliance in range(allianceDetails['alliance_size']):
            playerName = allianceDetails['members_list'][it_alliance]['Name']
            playerId = allianceDetails['members_list'][it_alliance]['Id']
            for it in range(len(colo_found_number)):
                if int(colo_found_number[it]["gl_id"]) == int(playerId): #renommer en id_gl dans db
                    await interaction.followup.send(f"> 🪐 **__(SB x):__**\n/colo_update pseudo:{playerName} colo_number:  colo_sys_name:  colo_coord_x:{colo_found_number[it]['X']} colo_coord_y:{colo_found_number[it]['Y']}\n")  
        
    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Colony(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])