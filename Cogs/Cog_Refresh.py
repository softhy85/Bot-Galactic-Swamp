import asyncio
import datetime
import discord
from discord import app_commands
from discord.ext import tasks, commands
from typing import List
import os
from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Player_Model import Player_Model
from Models.War_Model import Status, War_Model
from threading import Thread
class Cog_Refresh(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    war_status: Status = Status.Ended

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.war_channel_id: int = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.task_check_war_status.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Refresh")

    #</editor-fold>

    #<editor-fold desc="thread">
    
    def thread_update_players_online(self):
        date_start: datetime.datetime = datetime.datetime.now()
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None:
            war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", act_war["_alliance_id"])
            if war_alliance is not None:
                obj: dict = {"_alliance_id": act_war["_alliance_id"]}
                players: List[Player_Model] = list(self.bot.db.get_players(obj))
                for it in range(0, len(players)):
                    if "id_gl" in players[it]:
                        players[it]["online"] = self.bot.galaxyLifeAPI.get_player_status(players[it]['id_gl'])
                    else:
                        players[it]["online"] = 0
                    self.bot.db.update_player(players[it])
        date_end: datetime.datetime = datetime.datetime.now()
        print("Infos: players_online updated", "time :", date_end - date_start)
        print("Infos: task_update_players_online ended")        

    def thread_task_update_war_infos(self):
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None:
            war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", act_war["_alliance_id"])
            if war_alliance is not None:
                alliance_info = self.bot.galaxyLifeAPI.get_alliance(war_alliance["name"])
                if alliance_info != None:
                    war_alliance["alliance_lvl"] = alliance_info["alliance_lvl"]
                    war_alliance["alliance_winrate"] = alliance_info["alliance_winrate"]
                    war_alliance["emblem_url"] = alliance_info["emblem_url"]
                    war_alliance["score"] = alliance_info['alliance_score']
                else:
                    war_alliance["alliance_lvl"] = 0
                    war_alliance["alliance_winrate"] = "x"
                    war_alliance["emblem_url"] = ""
                    war_alliance["score"] = 0
                self.bot.db.update_alliance(war_alliance)
        print("Infos: task_update_war_infos ended") 
    
    def thread_task_update_players_level(self):
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None:
            war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", act_war["_alliance_id"])
            if war_alliance is not None:
                obj: dict = {"_alliance_id": act_war["_alliance_id"]}
                players: List[Player_Model] = list(self.bot.db.get_players(obj))
                for it_player in range(0, len(players)):
                    player_temp: dict = self.bot.galaxyLifeAPI.get_player_infos(players[it_player]["id_gl"])
                    players[it_player]["lvl"] = player_temp["lvl"]
                    players[it_player]["MB_lvl"] = player_temp["MB_lvl"]
                    self.bot.db.update_player(players[it_player])
                    obj: dict = {"_player_id": players[it_player]["_id"]}
                    colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
                    if len(colonies) != len(player_temp):
                        continue
                    colonies.sort(key=lambda item: item.get("number"), reverse = True)
                    for it_colo in range(0, len(player_temp["colo_list"])):
                        colonies[it_colo]["colo_lvl"] = player_temp["colo_list"][it_colo]
                        self.bot.db.update_colony(colonies[it_colo]) #ajouté récemment
        print("Infos: task_update_players_level ended")    
        
    def thread_task_update_base_status(self):
        print("Infos: task_update_base_status started")
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
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None:
            print(f"Info: Update at {date_time_str}")

        print("Infos: task_update_base_status ended")
        
    #</editor-fold>
    
    #<editor-fold desc="task">

        
    @tasks.loop(minutes=5) #TODO a threader
    async def task_update_war_infos(self):
        print("Infos: task_update_war_infos started")
        t: Thread = Thread(target=self.thread_task_update_war_infos)
        t.start()

    @tasks.loop(minutes=5) #TODO a threader
    async def task_update_players_level(self):
        print("Infos: task_update_players_level started")
        t: Thread = Thread(target=self.thread_task_update_players_level)
        t.start()

       

    # @tasks.loop(minutes=5)
    # async def task_update_players_online(self):
    #  
    #     date_start: datetime.datetime = datetime.datetime.now()
    #     act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
    #     if act_war is not None:
    #         war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", act_war["_alliance_id"])
    #         if war_alliance is not None:
    #             obj: dict = {"_alliance_id": act_war["_alliance_id"]}
    #             players: List[Player_Model] = list(self.bot.db.get_players(obj))
    #             for it in range(0, len(players)):
    #                 if "id_gl" in players[it]:
    #                     players[it]["online"] = self.bot.galaxyLifeAPI.get_player_status(players[it]['id_gl'])
    #                 else:
    #                     players[it]["online"] = 0
    #                 self.bot.db.update_player(players[it])
    #     date_end: datetime.datetime = datetime.datetime.now()
    #     print("Infos: Dashboard updated", "time :", date_end - date_start)
    #     print("Infos: task_update_players_online ended")        
        
    @tasks.loop(minutes=5)
    async def task_update_players_online(self):
        print("Infos: task_update_players_online started")
        t: Thread = Thread(target=self.thread_update_players_online)
        t.start()
                
    @tasks.loop(minutes=5) #TODO a threader
    async def task_update_base_status(self):
        print("Infos: task_update_base_status started")
        t: Thread = Thread(target=self.thread_task_update_base_status)
        t.start()

    @tasks.loop(minutes=1)
    async def task_check_war_status(self):
        print("Infos: task_check_war_status")     
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        print(act_war)
        if act_war is not None and self.war_status == Status.Ended:
            self.war_status = Status.InProgress
            self.task_update_war_infos.start()
            self.task_update_players_level.start()
            self.task_update_players_online.start()
            self.task_update_base_status.start() 
        elif self.war_status == Status.InProgress:  
            self.war_status = Status.Ended
            self.task_update_war_infos.stop()
            self.task_update_players_level.stop()
            self.task_update_players_online.stop()
            self.task_update_base_status.stop()


    #<editor-fold desc="task on ready">

    @task_update_war_infos.before_loop
    async def before_task_update_war_infos(self):
        await self.bot.wait_until_ready()

    @task_update_players_level.before_loop
    async def before_task_update_players_level(self):
        await self.bot.wait_until_ready()

    @task_update_players_online.before_loop
    async def before_task_update_players_online(self):
        await self.bot.wait_until_ready()        
        
    @task_update_base_status.before_loop
    async def before_task_update_base_status(self):
        await self.bot.wait_until_ready()
        
    @task_check_war_status.before_loop
    async def before_task_check_war_status(self):
        await self.bot.wait_until_ready()

    #</editor-fold>
    
    #</editor-fold>


async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Refresh(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])