import datetime
import os
import re
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from Models.Colony_Model import Colony_Model
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model
from Utils.Autocomplete import Autocomplete


class Cog_Colony(commands.Cog):
    guild: discord.Guild = None
    bot: commands.bot = None
    autocomplete = Autocomplete
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
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Colony")

    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="colo_update", description="Update a saved colony")
    @app_commands.describe(pseudo="Player's username", colo_number="if not found : ✅ run /player_infos and add its alliance ", colo_sys_name="Colony's system name (in CAPS)", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=autocomplete.player_war_autocomplete, colo_number=autocomplete.colo_autocomplete)
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

    @app_commands.command(name="move_colony", description="tell the bot you moved a leaked")
    @app_commands.describe(colo_number="if not found : ✅ run /player_infos and add its alliance ")
    # @app_commands.autocomplete(pseudo=autocomplete.player_ally_autocomplete, colo_number=autocomplete.colo_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def move_colony(self, interaction: discord.Interaction, colo_number: int):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("> 🚫 You don't have the permission to use this command.")
            return
        else:
            leaked_colonies = self.bot.db.get_leaked_colonies()
            print(leaked_colonies)
            name = interaction.user.name

            if f"{name}" in leaked_colonies:
                print(leaked_colonies[name])
                for enemy in leaked_colonies[name]:
                    if enemy != 'last_update' and enemy != 'registered_users':
                        print(leaked_colonies[name][enemy])
                        
                        leaked_colonies[name][enemy].remove(f"{colo_number}")
            print(leaked_colonies)
            await interaction.response.send_message(f"> Colony n°**{colo_number}** of **{name}** moved. ✅")
            self.bot.db.update_leaked_colonies(leaked_colonies)
                
 
    @app_commands.command(name="colo_gift", description="Gift colony to low level players / Or tell if a colony never has defenses")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="Wich colony", gift_state="x")
    @app_commands.autocomplete(pseudo=autocomplete.player_war_autocomplete, colo_number=autocomplete.colo_autocomplete,  gift_state=autocomplete.gift_state_autocomplete)
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

            
    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Colony(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])