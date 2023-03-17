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
        alliances = self.bot.db.get_all_alliances()
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
            
    # Pas très sûr de moi: je veux que l'utilisateur puisse choisir le numéro de colonie. Si la colonie est déjà remplie, un coche ✅ (colo["completion"]) s'affiche devant. Autre possibilité: n'afficher que les colonies non remplies       
    # Il faut recup le joueur 
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

    @app_commands.command(name="colo_add", description="Add a new Colony to the db")
    @app_commands.describe(pseudo="Player's pseudo", colo_sys_name="Colony's system name", colo_lvl="Colony's level", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_war_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colo_add(self, interaction: discord.Interaction, pseudo: str, colo_sys_name: str, colo_lvl: int, colo_coord_x: int, colo_coord_y: int):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is None:
            await interaction.response.send_message("No war in progress, to add a colony with a specific player out of war, use /colony_scout.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            date: datetime.datetime = datetime.datetime.now()
            obj: dict = {"_player_id": act_player["_id"]}
            number: int = self.bot.db.db.colonies.count_documents(obj)
            new_colony: Colony_Model = {"_alliance_id": act_player["_alliance_id"], '_player_id': act_player["_id"], 'number': number + 1, 'colo_sys_name': str.upper(colo_sys_name), 'colo_lvl': colo_lvl, 'colo_coord': {"x": colo_coord_x, "y": colo_coord_y}, 'colo_status': "Up", 'colo_last_attack_time': date, 'colo_refresh_time': date}
            self.bot.db.push_new_colony(new_colony)
            await interaction.response.send_message(f"A colony as been added to Player named {pseudo}.")
            await self.bot.dashboard.update_Dashboard()
###
    @app_commands.command(name="colo_scout", description="Add a new Colony to the db")
    @app_commands.describe(pseudo="Player's pseudo", colo_sys_name="Colony's system name", colo_lvl="Colony's level", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_autocomplete)
    @app_commands.checks.has_any_role('Admin', 'Assistant')
    async def colo_scout(self, interaction: discord.Interaction, pseudo: str, colo_sys_name: str, colo_lvl: int, colo_coord_x: int, colo_coord_y: int):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user) and not self.bot.spec_role.assistant_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        act_player: Player_Model = self.bot.db.get_one_player("pseudo", pseudo)
        if act_player is None:
            await interaction.response.send_message(f"Player named {pseudo} not found.")
        else:
            date: datetime.datetime = datetime.datetime.now()
            obj: dict = {"_player_id": act_player["_id"]}
            number: int = self.bot.db.db.colonies.count_documents(obj)
            new_colony: Colony_Model = {"_alliance_id": act_player["_alliance_id"], '_player_id': act_player["_id"], 'number': number + 1, 'colo_sys_name': str.upper(colo_sys_name), 'colo_lvl': colo_lvl, 'colo_coord': {"x": colo_coord_x, "y": colo_coord_y}, 'colo_status': "Up", 'colo_last_attack_time': date, 'colo_refresh_time': date}
            self.bot.db.push_new_colony(new_colony)
            await interaction.response.send_message(f"A colony as been added to Player named {pseudo}.")
            await self.bot.dashboard.update_Dashboard()
            
    # Retravaillée car les infos à fournir ont changé
    @app_commands.command(name="colo_update", description="Update an existent Colony")
    @app_commands.describe(pseudo="Player's pseudo", colo_number="the number of the colony", colo_sys_name="Colony's system name (in CAPS)", colo_coord_x="Colony's x coordinate", colo_coord_y="Colony's y coordinate")
    @app_commands.autocomplete(pseudo=player_autocomplete, colo_number=colo_autocomplete)
    @app_commands.default_permissions()
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
                await interaction.response.send_message(f"Colony updated.")
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Colony(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])