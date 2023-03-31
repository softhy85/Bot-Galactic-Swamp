import discord
from discord import app_commands
from discord.ext import commands
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from models.Colors import Colors
from typing import List
import os
import re


class Alliance(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.log_channel_id: int = int(os.getenv("COLO_BACKUP_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Alliance")

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

    @app_commands.command(name="alliance_add", description="Add a new Alliance to the db")
    @app_commands.describe(alliance="The name of the alliance")
    @app_commands.checks.has_role('Admin')
    @app_commands.default_permissions()
    async def alliance_add(self, interaction: discord.Interaction, alliance: str):
        self.log_channel_id: int = int(os.getenv("COMMAND_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)
            
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot create alliances with a name composed only of whitespace.")
            return
        add_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        if add_alliance is None:
            if self.bot.galaxylifeapi.get_alliance(alliance) is None:
                await interaction.response.send_message(f"{alliance} doesn't seem to exist")
                return
            else:
                new_alliance: Alliance_Model = {"name": alliance.upper()}
                new_alliance["_id"] = self.bot.db.push_new_alliance(new_alliance)
                if new_alliance["_id"] is None:
                    await interaction.response.send_message(f"Something goes wrong while creating the Alliance {alliance}.\nPlease report this bug to @Softy(léo).")
                    return
                add_alliance = new_alliance
        ennemy = self.bot.galaxylifeapi.get_alliance(alliance)
        await interaction.response.send_message("> Loading alliance...")  
        # Création du joueur et de sa main base
        alliance_info = self.bot.galaxylifeapi.get_alliance(alliance)
        obj: dict = {"_alliance_id": add_alliance["_id"]}
        db_players: List[Player_Model] = self.bot.db.get_players(obj)
        for db_player in db_players:
            for player in alliance_info["members_list"]:
                if db_player["pseudo"] != player["Name"]:
                    db_player["_alliance_id"] = None
                    self.bot.db.update_player(db_player)
        for player in alliance_info["members_list"]:
            new_player: Player_Model = {'_alliance_id': add_alliance["_id"], 'pseudo': player["Name"], 'id_gl': player["Id"], 'bunker_full': False}
            act_player: Player_Model =  self.bot.db.push_new_player(new_player)
            if act_player == None:
                act_player = self.bot.db.get_one_player("pseudo", player["Name"])
                if act_player["_alliance_id"] != add_alliance["_id"]:
                    act_player["_alliance_id"] = add_alliance["_id"]
                    act_player['id_gl'] = player['Id']
                    self.bot.db.update_player(act_player)        
            else:
                act_player = self.bot.db.get_one_player("pseudo", player["Name"])
                act_player['id_gl'] = player['Id']
                self.bot.db.update_player(act_player)
            colo_list: list = self.bot.galaxylifeapi.get_player_infos(player["Id"])["colo_list"]
            it: int = 0
            if len(colo_list) != 0:
                for colo in colo_list:
                    colo_level = colo_list[it]
                    colo_number = len(colo_list) 
                    obj: dict = {"_player_id": act_player["_id"]}
                    new_colony: Colony_Model = {"_alliance_id": add_alliance["_id"], '_player_id': act_player["_id"], 'number': it + 1, 'colo_sys_name': "-1", 'colo_lvl': colo_level, 'colo_coord': {"x": '-1', "y": '-1'}, 'colo_status': "Up", 'updated': False, 'gift_state': "Not Free"} 
                    stored_colony: List[Colony_Model] = list(self.bot.db.get_colonies({"_player_id": act_player["_id"], "number": it + 1}))
                    if len(stored_colony) == 1: 
                        new_colony["_id"] = stored_colony[0]["_id"]
                        new_colony["colo_sys_name"] = stored_colony[0]["colo_sys_name"]
                        new_colony["colo_coord"] = stored_colony[0]["colo_coord"]
                        if "updated" in stored_colony:
                            new_colony["updated"] = stored_colony[0]["updated"]
                        else:
                            new_colony["updated"] = False
                        self.bot.db.update_colony(new_colony)
                        #await self.log_channel.send(f"Colony number {it + 1} was updated for Player named **{player['Name']}**.")
                    elif len(stored_colony) == 0: 
                        self.bot.db.push_new_colony(new_colony)
                       # await self.log_channel.send(f"Colony number {it + 1} was added to Player named **{player['Name']}**.")
                    else:
                        new_colony["_id"] = stored_colony[0]["_id"]
                        self.bot.db.update_colony(new_colony)
                        await self.log_channel.send(f"Some duplicate colonies was found for **{player['Name']}**. Updating the first one.")
                        stored_colony = stored_colony[1:]
                        for colony in stored_colony:
                            self.bot.db.remove_colony(colony)
                    if it == len(colo_list):
                        break  
                    it += 1
                #await self.log_channel.send(f"> **{colo_number}** 🪐 colonies were added or updated for Player named __**{player['Name']}**__.")
            else: 
                await self.log_channel.send(f"> No colony was added to Player named __**{player['Name']}**__.")    
        # Communication et création du Thread    
        await self.log_channel.send("> Alliance Added")

        


   

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

    @app_commands.command(name="alliance_colonies", description="Get all colonies from an alliance")
    @app_commands.describe(alliance="Alliance's name")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_any_role('Admin')
    async def alliance_colonies(self, interaction: discord.Interaction,  alliance: str): 
        alliance_info: Alliance_Model = self.bot.db.get_one_alliance("name", alliance)
        alliance_api_info = self.bot.galaxylifeapi.get_alliance(alliance_info["name"])
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
                if colo['colo_coord']['x'] != "-1":
                    value = value + f"\n🪐 **__(SB{colo['colo_lvl']}):__**\n/colo_update pseudo:{player['pseudo']} colo_number:{colo['number']} colo_sys_name:{colo['colo_sys_name']} colo_coord_x:{colo['colo_coord']['x']} colo_coord_y:{colo['colo_coord']['y']}\n"
            if value != "": 
                embed.add_field(name=f"\n✅ {player['pseudo']}",value=value, inline=False)
                field_count += 1
        
            total_size += len(value) + len(player) + 5
            if total_size >= 2500 or field_count >= 20:
                await self.log_channel.send(embed=embed)
                embed: discord.Embed = discord.Embed(title="", description="", color=discord.Color.from_rgb(8, 1, 31)) 
                total_size: int = 0
                field_count: int = 0
        if total_size != 0:
            await self.log_channel.send(embed=embed)
                      
               
       

async def setup(bot: commands.Bot):
    await bot.add_cog(Alliance(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])