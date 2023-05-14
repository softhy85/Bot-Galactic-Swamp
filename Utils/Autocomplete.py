import re
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Emoji import Emoji
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model


class Autocomplete:
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

    async def player_db_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
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
    
    async def gift_state_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]: 
        data = []
        for choice in ["Always Free","Free Once", "Not Free"]:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data