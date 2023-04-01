import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
from Models.War_Model import War_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.Alliance_Model import Alliance_Model
from Models.Emoji import Emoji
from Models.Colors import Colors
from typing import List
import os
import re

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
        self.task_update_colonies.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Colony")


    #</editor-fold>

    #<editor-fold desc="autocomplete">

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
        pseudo = interaction.namespace.pseudo
        player_id: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile(pseudo, re.IGNORECASE)})  
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

    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="colo_infos", description="Display the infos of the Colonies of a Cog_Player")
    @app_commands.describe(pseudo="Player's pseudo")
    @app_commands.autocomplete(pseudo=player_autocomplete)
    async def colo_infos(self, interaction: discord.Interaction, pseudo: str):
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot retreive infos of a Cog_Player with a pseudo composed only of whitespace.")
            return
        player: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile(pseudo, re.IGNORECASE)})
        if player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies({"_player_id": player['_id']}))
            if len(colonies) == 0:
                await interaction.response.send_message(f"Colonies not found.")
            else:
                embed: discord.Embed
                embed = discord.Embed(title=f"Niv  : { player['pseudo'] }️", description="", color=Colors.gold, timestamp=datetime.datetime.now())
                it: int = 1
                for colony in colonies:
                    if colony['colo_sys_name'] != "-1":
                        embed.add_field(name=f"{ Emoji.colo.value if colony['colo_status'] == 'Up' else Emoji.down.value } Colonie {it} : {colony['colo_sys_name']}",value=f"({colony['colo_coord']['x']} ; {colony['colo_coord']['y']}) - SB ({colony['colo_lvl']})", inline=False)
                    it += 1
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="colo_update", description="Update an existent Cog_Colony")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="the number of the colony", colo_sys_name="Colony's system name (in CAPS)", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colo_update(self, interaction: discord.Interaction, pseudo: str, colo_number: int, colo_sys_name: str = "", colo_coord_x: int = -1, colo_coord_y: int = -1):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if pseudo.strip() == "":
            await interaction.response.send_message(f"Cannot remove a Cog_Colony from Players with a pseudo composed only of whitespace.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", {"$regex": re.compile(pseudo, re.IGNORECASE)})
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
                # await self.bot.dashboard.update_Dashboard()

    # @app_commands.command(name="colony_remove", description="Remove an existent Cog_Colony")
    # @app_commands.describe(pseudo="Player's pseudo", colo_number="the number of the colony")
    # @app_commands.autocomplete(pseudo=player_autocomplete)
    # @app_commands.checks.has_any_role('Admin', 'Assistant')
    # async def colony_remove(self, interaction: discord.Interaction, pseudo: str, colo_number: int,):
    #     if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
    #         await interaction.response.send_message("You don't have the permission to use this command.")
    #         return
    #     if pseudo.strip() == "":
    #         await interaction.response.send_message(f"Cannot remove a Cog_Colony from Players with a pseudo composed only of whitespace.")
    #         return
    #     act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
    #     if act_player is None:
    #         await interaction.response.send_message(f"Player named {pseudo} not found.")
    #     else:
    #         obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
    #         act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
    #         if act_colony is None:
    #             await interaction.response.send_message(f"Colony not found.")
    #         else:
    #             self.bot.db.remove_colony(act_colony[0])
    #             await interaction.response.send_message(f"Player named {pseudo} as been removed.")
    #             await self.bot.dashboard.update_Dashboard()

    @app_commands.command(name="gift_colony", description="Gift colony to low level players / Or tell if a colony never has defenses")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="Wich colony", gift_state="x")
    @app_commands.autocomplete(pseudo=player_war_autocomplete, colo_number=colo_autocomplete,  gift_state=gift_state_autocomplete)
    async def gift_colony(self, interaction: discord.Interaction, pseudo: str,colo_number: int, gift_state: str):
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        obj: dict = {"_player_id": act_player['_id'], "number": colo_number}
        act_colony: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} does not exist.")
        else:
            act_colony = act_colony[0]
            act_colony["gift_state"]: str = gift_state
            self.bot.db.update_colony(act_colony)
            await self.log_channel.send(f"> <@&1089184438442786896> a new free colony has been added !! 🎁") #j'ai juste changé l'ordre
            await self.bot.dashboard.update_Dashboard()
            await interaction.response.send_message(f"The free state of colony n°{act_colony['number']} of {pseudo} has been updated.")

    #</editor-fold>

    #<editor-fold desc="task">

    @tasks.loop(minutes=5)
    async def task_update_colonies(self):
        print("Infos: task_update_colonies started")
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        obj: dict = {"MB_status": "Down"}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        for player in players:
            date_next: datetime.datetime = player["MB_refresh_time"]
            if now > date_next:
                player["MB_status"] = "Up"
                self.bot.db.update_player(player)
        obj = {"colo_status": "Down"}
        colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        for colony in colonies:
            date_next: datetime.datetime = colony["colo_refresh_time"]
            if now > date_next:
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            print(f"Info: Update at {date_time_str}")
            await self.bot.dashboard.update_Dashboard()
        print("Infos: task_update_colonies ended")

    @task_update_colonies.before_loop
    async def before_task_update_colonies(self):
        await self.bot.wait_until_ready()

    #</editor-fold>

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Colony(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])