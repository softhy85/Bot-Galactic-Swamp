import discord
from discord import app_commands
from datetime import datetime
import discord
from discord import Embed, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext import tasks, commands
from models.War_Model import War_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from models.War_Model import War_Model, Status
from pymongo.cursor import Cursor
from typing import List
import os
from models.Alliance_Model import Alliance_Model
import json


class RefreshInfos(commands.Cog):
    guild: discord.Guild
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        self.update_Info_Base.start()
        self.experiment_channel_id: int = int(os.getenv("EXPERIMENT_CHANNEL"))
        self.experiment_channel = self.bot.get_channel(self.experiment_channel_id)
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id: int = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.war_channel_id)
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
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            await self.is_war_over(actual_war)
        else:
            await self.is_war_started()
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
            
            
    async def is_war_over(self, actual_war, status: Status = Status.InProgress):
        ennemy = self.bot.galaxylifeapi.get_alliance(actual_war["alliance_name"])
        
        actual_date = datetime.now()
        if ennemy["war_status"] == False:
            war_thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
            obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
            players: List[Player_Model] = list(self.bot.db.get_players(obj))
            ally_alliance = self.bot.galaxylifeapi.get_alliance("GALACTIC SWAMP")
            war_progress = self.bot.dashboard.war_progress(actual_war["alliance_name"], players)
            if "start_time" in actual_war:
                converted_start_time = datetime.strftime(actual_war["start_time"],  "%Y/%m/%d %H:%M:%S.%f")
                strp_converted_start_time = datetime.strptime(converted_start_time, "%Y/%m/%d %H:%M:%S.%f")
                converted_actual_date = datetime.strftime(actual_date,  "%Y/%m/%d %H:%M:%S.%f")
                strp_converted_actual_date = datetime.strptime(converted_actual_date, "%Y/%m/%d %H:%M:%S.%f")
                delta = strp_converted_actual_date - strp_converted_start_time
                days, seconds = delta.days, delta.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                await self.experiment_channel.send(f"War has ended after a duration of {hours} hours, {minutes} minutes and {seconds} seconds. Score: {war_progress['ally_alliance_score']} VS {war_progress['ennemy_alliance_score']} - Team members: {ally_alliance['alliance_size']} VS {war_progress['main_planet']}")
            else: 
                hours = "x"
                minutes = "x"
                seconds = "x"
                await self.experiment_channel.send(f"War has ended after a duration of {hours} hours, {minutes} minutes and {seconds} seconds. Score: {war_progress['ally_alliance_score']} VS {war_progress['ennemy_alliance_score']} - Team members: {ally_alliance['alliance_size']} VS {war_progress['main_planet']}")

            if war_thread is not None:
                if int(war_progress['ally_alliance_score']) and int(war_progress['ennemy_alliance_score']) != 0:
                    if int(war_progress['ally_alliance_score']) > int(war_progress['ennemy_alliance_score']):
                        actual_war["status"] = "Win"
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Won",archived=True, locked=True)
                        await self.general_channel.send(f"War against {actual_war['alliance_name']} has been won.")
                    elif int(war_progress['ally_alliance_score']) < int(war_progress['ennemy_alliance_score']):
                        actual_war["status"] = 'Lost'
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Lost",archived=True, locked=True)
                        await self.general_channel.send(f"War against {actual_war['alliance_name']} has been lost.")
                else: 
                    actual_war["status"] = "Ended"
                    await war_thread.edit(name=f"{actual_war['alliance_name']} - Over",archived=True, locked=True)
                    await self.general_channel.send(f"War against {actual_war['alliance_name']} is now over.")
            else:
                await self.general_channel.send(f"War against {actual_war['alliance_name']} is now over.")
            print("war ended")
            self.bot.db.update_war(actual_war)
        else: 
            print("war still ongoing.")
        return
    
    async def is_war_started(self):
        alliance = "GALACTIC SWAMP"
        alliance_infos = self.bot.galaxylifeapi.get_alliance(alliance)
        if alliance_infos['war_status'] == True:
            await self.bot.war.new_war(alliance_infos["ennemy_name"].upper())         
            
async def setup(bot: commands.Bot):
    await bot.add_cog(RefreshInfos(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])