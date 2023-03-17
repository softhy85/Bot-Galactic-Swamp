import discord
from discord import app_commands
from datetime import datetime
import requests
from discord.ext import tasks, commands
from models.War_Model import War_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from pymongo.cursor import Cursor
from typing import List
import os
from models.Alliance_Model import Alliance_Model
import json


class RefreshInfos(commands.Cog):
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_Info_Base.start()
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print("RefreshInfos cog loaded.")

    def cog_unload(self):
        self.update_Info_Base.cancel()

    @tasks.loop(minutes=1)
    async def update_Info_Base(self) -> int:
        now = datetime.now()
        date_time_str = now.strftime("%H:%M:%S")
        print(f"Update at {date_time_str}")
        obj: dict = {"MB_status": "Down"}
        players: Cursor[Player_Model] = self.bot.db.get_players(obj)
        for player in players:
            date: datetime = datetime.now()
            date_next: datetime.datetime = player["MB_refresh_time"]
            if date > date_next:
                player["MB_status"] = "Up"
                self.bot.db.update_player(player)
        obj = {"colo_status": "Down"}
        colonies: Cursor[Colony_Model] = self.bot.db.get_colonies(obj)
        for colony in colonies:
            date: datetime = datetime.now()
            date_next: datetime.datetime = colony["colo_refresh_time"]
            if date > date_next:
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        
        # #### update du status des joueurs
        # alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])    
        # player: Player_Model = self.bot.db.get_players(obj)
        
        # for i in alliance['player_number']:
        #     steamId = player['_steam_id']
        #     steamPlayerState = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=B8D87A555C403CD7C16250A103F3A5E7&format=json&steamids={steamId}')
        #     # A POURSUIVRE: RECUPERATION DES ID de JOUEURS
        #     parsed_steamPlayerState = json.loads(steamPlayerState.content)
        #     playerSteamStatus = parsed_steamPlayerState['response']['players'][0]['personastate']
            
        #     if playerSteamStatus == 1:
        #         if "gameextrainfo" in parsed_steamPlayerState['response']['players'][0]:
        #             if parsed_steamPlayerState['response']['players'][0]['gameextrainfo'] == "Galaxy Life":   
                        
        #                 playerStatus = "Online"
        #         else:
        #             playerStatus = "Offline"
        #     else: 
        #         playerStatus = "Offline"
        #     i = i + 1
            
            
        if actual_war is not None:
            await self.bot.dashboard.update_Dashboard()
            
            
            
            
async def setup(bot: commands.Bot):
    await bot.add_cog(RefreshInfos(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])