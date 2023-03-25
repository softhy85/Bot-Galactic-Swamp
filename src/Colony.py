import datetime
import discord
from discord import app_commands
from discord.ext import commands
from models.War_Model import War_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from models.Alliance_Model import Alliance_Model
from models.Emoji import Emoji
from models.Colors import Colors
from typing import List
import os
import re


class Colony(commands.Cog):
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
        print("Player cog loaded.")

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

    async def player_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is None:
            return []
        else:
            obj: dict = {"_alliance_id": act_war["_alliance_id"]}
            players: List[Player_Model] = self.bot.db.get_players(obj)
            return [
                app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
                for player in players
            ]
            
    async def  colo_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is None:
            return []
        else:
            pseudo = interaction.namespace.pseudo
            player_id: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
            obj: dict = {"_player_id": player_id['_id']}
            colos: List[Colony_Model] = self.bot.db.get_colonies(obj)     
            colos = colos[0:25]
            return [
                app_commands.Choice(name=f'{Emoji.updated.value if colo["updated"] else Emoji.native.value} Colo n°{colo["number"]} (SB{colo["colo_lvl"]})', value=colo["number"])
                for colo in colos
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
            print(players)
            players = players[0:25]
            return [
                app_commands.Choice(name=player["pseudo"], value=player["pseudo"])
                for player in players
            ]
            
    async def gift_state_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]: 
        data = []
        for choice in ["Always Free","Free Once", "Not Free"]:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data   
    
    @app_commands.command(name="colo_update", description="Update an existent Colony")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="the number of the colony", colo_sys_name="Colony's system name (in CAPS)", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colo_update(self, interaction: discord.Interaction, pseudo: str, colo_number: int, colo_sys_name: str, colo_coord_x: int, colo_coord_y: int):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot remove a Colony from Players with a pseudo composed only of whitespace.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            act_colony: List[Colony_Model] = list(self.bot.db.get_colonies({"_player_id": act_player['_id'], "number": colo_number}))
            if len(act_colony) == 0:
                await interaction.response.send_message(f"Colony not found.")
            else:
                act_colony = act_colony[0]
                if colo_sys_name != "":
                    act_colony["colo_sys_name"] = colo_sys_name
                if colo_coord_x != -1:
                    act_colony["colo_coord"]["x"] = colo_coord_x
                if colo_coord_y != -1:
                    act_colony["colo_coord"]["y"] = colo_coord_y
                act_colony["updated"] = True
                self.bot.db.update_colony(act_colony)
                await interaction.response.send_message(f"Colony n°{colo_number} of {pseudo} updated.")
                await self.bot.dashboard.update_Dashboard()


    @app_commands.command(name="colony_remove", description="Remove an existent Colony")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="the number of the colony")
    @app_commands.autocomplete(pseudo=player_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colony_remove(self, interaction: discord.Interaction, pseudo: str, colo_number: int,):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot remove a Colony from Players with a pseudo composed only of whitespace.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
            act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            if act_colony is None:
                await interaction.response.send_message(f"Colony not found.")
            else:
                self.bot.db.remove_colony(act_colony[0])
                await interaction.response.send_message(f"Player named {pseudo} as been removed.")
                await self.bot.dashboard.update_Dashboard()

    @app_commands.command(name="gift_colony", description="Gift colony to low level players / Or tell if a colony never has defenses")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="Wich colony", gift_state="x")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete,  gift_state=gift_state_autocomplete)
    async def player_bunkers(self, interaction: discord.Interaction, pseudo: str,colo_number: int, gift_state: str):
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
        act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} does not exist.")
        else:
            act_colony = act_colony[0]
            act_colony["gift_state"]: str = gift_state
            self.bot.db.update_colony(act_colony)
            await interaction.response.send_message(f"The free state of colony n°{act_colony['number']} of {pseudo} has been updated.")
            await self.log_channel.send(f"> <@&1089184438442786896> a new free colony has been added !! 🎁")
            await self.bot.dashboard.update_Dashboard()
            
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Colony(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])