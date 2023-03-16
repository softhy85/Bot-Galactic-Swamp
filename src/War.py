import discord
from discord import Embed, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from models.Alliance_Model import Alliance_Model
from models.War_Model import War_Model, Status
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from typing import List
import os
import requests
import json
import datetime
import time

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
    @app_commands.describe(alliance="The name of the alliance against which you are at war")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    @app_commands.default_permissions()
    async def war_new(self, interaction: discord.Interaction, alliance: str):
        date: datetime.datetime = datetime.datetime.now()
        self.log_channel_id: int = int(os.getenv("COMMAND_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)
            
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot create alliances with a name composed only of whitespace.")
            return
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            await interaction.response.send_message(f"We are already at war with {actual_war['alliance_name']}.")
            return
        
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if war_alliance is None:
            if self.bot.galaxylifeapi.get_alliance(alliance) is None:
                await interaction.response.send_message(f"{alliance} doesn't seem to exist")
                return
            else:
                new_alliance: Alliance_Model = {"name": alliance}
                new_alliance["_id"] = self.bot.db.push_new_alliance(new_alliance)
                if new_alliance["_id"] is None:
                    await interaction.response.send_message(f"Something goes wrong while creating the Alliance {alliance}.\nPlease report this bug to @Softy(léo).")
                    return
                war_alliance = new_alliance
        await interaction.response.send_message("> Loading alliance...")
        
            
        # Création du joueur et de sa main base
        alliance_info = self.bot.galaxylifeapi.get_alliance(alliance)
        for player in alliance_info["members_list"]:
            print("OK 1")
            
            new_player: Player_Model = {'_alliance_id': war_alliance["_id"], 'pseudo': player["Name"], '_gl_id': player["Id"], 'MB_status': 'Up', 'MB_last_attack_time': date, 'MB_refresh_time': date}
            act_player: Player_Model =  self.bot.db.push_new_player(new_player)
            if act_player == None:
                act_player = self.bot.db.get_one_player("pseudo", player["Name"])
                await self.log_channel.send(f"> Player named __**{player['Name']}**__ recovered.")
            else:
                await self.log_channel.send(f"> Player named __**{player['Name']}**__ created.")
            print("OK 2")
            # Récupération des niveaux des colonies et création des colonies
            colo_list: list = self.bot.galaxylifeapi.get_player_infos(player["Id"])["colo_list"]
            it: int = 1
            print("OK 2.1")
            for colo in colo_list:
                print(colo)
                print(colo_list)
                print(it)
                colo_level = colo_list[it]
                colo_number = len(colo_list) 
                obj: dict = {"_player_id": act_player["_id"]}
                number: int = self.bot.db.db.colonies.count_documents(obj) #?
                new_colony: Colony_Model = {"_alliance_id": war_alliance["_id"], '_player_id': act_player["_id"], 'number': it, 'colo_sys_name': "-1", 'colo_lvl': colo_level, 'colo_coord': {"x": '-1', "y": '-1'}, 'colo_status': "Up", 'colo_last_attack_time': date, 'colo_refresh_time': date}
                stored_colony: List[Colony_Model] = list(self.bot.db.get_colonies({"_player_id": act_player["_id"], "number": it}))
                if len(stored_colony) == 1: 
                    new_colony["_id"] = stored_colony[0]["_id"]
                    self.bot.db.update_colony(new_colony)
                    #await self.log_channel.send(f"Colony number {it} was updated for Player named **{player['Name']}**.")
                elif len(stored_colony) == 0: 
                    self.bot.db.push_new_colony(new_colony)
                    #await self.log_channel.send(f"Colony number {it} was added to Player named **{player['Name']}**.")
                else:
                    new_colony["_id"] = stored_colony[0]["_id"]
                    self.bot.db.update_colony(new_colony)
                    await self.log_channel.send(f"Some duplicate colonies was found for **{player['Name']}**. Updating the first one.")
                    stored_colony = stored_colony[1:]
                    for colony in stored_colony:
                        self.bot.db.remove_colony(colony)
                it += 1
                if it == len(colo_list):
                    break  
                
            await self.log_channel.send(f"> **{colo_number}** 🪐 colonies were added or updated for Player named __**{player['Name']}**__.")
            
        # Communication et création du Thread    
        await self.log_channel.send("> New war started.")
        new_message: discord.Message = await self.war_channel.send(f"Nous sommes en guerre contre **{war_alliance['name']}** !!")
        new_thread: discord.Thread = await new_message.create_thread(name=war_alliance["name"])
        new_war: War_Model = {"_alliance_id": war_alliance["_id"], "alliance_name": war_alliance["name"], "id_thread": new_thread.id, "enemy_point": 0, "point": 0, "status": "InProgress"}
        new_war["_id"] = self.bot.db.push_new_war(new_war)
        await self.bot.dashboard.create_Dashboard(new_war)

    @app_commands.command(name="war_update", description="Update the actual war")
    @app_commands.describe(status="Status",point="The point of our alliance", enemy_point="The point of the enemy alliance")
    @app_commands.checks.has_role('Admin')
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
                    await self.general_channel.send(f"La guerre actuelle contre {actual_war['alliance_name']} a été gagnée.")
                if status.value == 3:
                    if war_thread is not None:
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Lost",archived=True, locked=True)
                    await self.general_channel.send(f"La guerre actuelle contre {actual_war['alliance_name']} a été perdue.")
                if status.value == 4:
                    if war_thread is not None:
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Ended",archived=True, locked=True)
                    await self.general_channel.send(f"La guerre actuelle contre {actual_war['alliance_name']} est terminée.")

async def setup(bot: commands.Bot):
    await bot.add_cog(War(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])