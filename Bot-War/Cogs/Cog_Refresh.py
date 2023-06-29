import asyncio
import datetime
import os
from threading import Thread
from typing import List

import discord
from discord import app_commands
from discord.ext import commands, tasks

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Player_Model import Player_Model
from Models.War_Model import Status, War_Model


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
        if not  self.task_check_war_status.is_running():
            self.task_check_war_status.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Refresh")

    #</editor-fold>

    #<editor-fold desc="thread">
    
    def thread_update_players(self):
        print('updating players')
        date_start: datetime.datetime = datetime.datetime.now()
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None:
            war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", act_war["_alliance_id"])
            enemy_alliance: dict = self.bot.galaxyLifeAPI.get_alliance(war_alliance['name'])
            if war_alliance is not None:
                obj: dict = {"_alliance_id": act_war["_alliance_id"]}
                # players: List[Player_Model] = list(self.bot.db.get_players(obj))
                it = 0
                for member in enemy_alliance['members_list']:
                    player = self.bot.db.get_one_player("pseudo", member['Name'])
                    if "id_gl" in player:
                        player["online"] = self.bot.galaxyLifeAPI.get_player_status(player['id_gl'])
                    else:
                        player["online"] = None
                    player_war_info: dict = next(item for item in enemy_alliance['members_list'] if item["Name"] == f"{player['pseudo']}")
                    # print(player_war_info)
                    if player['total_war_points'] < player_war_info['WarPoints']:
                        player['war_points_delta'] = int(player_war_info['WarPoints']) - int(player['total_war_points'])
                        player['total_war_points'] = player_war_info['WarPoints']
                        player['last_attack_time'] = date_start
                    if player["online"] is None or player["online"] == 1:
                        if player['last_attack_time'] + datetime.timedelta(minutes=15) > date_start:
                            player["online"] = 2
                        else: 
                            player["online"] = 0
                    self.bot.db.update_player(player)
                    it += 1
                    player_temp: dict = self.bot.galaxyLifeAPI.get_player_infos(player["id_gl"])
                    player_stats: dict = self.bot.galaxyLifeAPI.get_player_stats(player["id_gl"])
                    if "colonies_moved" in player:
                        if player["colonies_moved"] !=  player_stats["colonies_moved"]:
                            player["colonies_moved"] = player_stats["colonies_moved"]
                            player_temp["colonies_moved_bool"] = True
                    player["lvl"] = player_temp["lvl"]
                    player["MB_lvl"] = player_temp["MB_lvl"]
                    self.bot.db.update_player(player)
                    obj: dict = {"_player_id": player["_id"]}
                    colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
                    # if len(colonies) != len(player_temp['colo_list']):
                    #     continue
                    colonies.sort(key=lambda item: item.get("number"), reverse = False)
                    # if player["id_gl"] == 85029:
                        # print(f"-----------> colonies:{colonies}\nplayer temp: {player_temp['colo_list']}")
                    # print('if gone')
                    for it_colo in range(0, len(player_temp["colo_list"])): 
                        if it_colo < len(colonies):
                            # print(len(colonies))
                            # # print(colonies[it_colo], player_temp['colo_list'])
                            # print(player["id_gl"])
                            colonies[it_colo]["colo_lvl"] = player_temp["colo_list"][it_colo]
                            self.bot.db.update_colony(colonies[it_colo]) #ajouté récemment
                        else:
                            # print(colonies[it_colo-1])
                            # print(player_temp["colo_list"][it_colo])
                            new_colony: Colony_Model = {"_alliance_id": player["_alliance_id"], 'id_gl': player["id_gl"], '_player_id': player['_id'], 'number': it_colo, 'colo_sys_name': "?", 'colo_lvl': player_temp["colo_list"][it_colo], 'colo_coord': {"x": -1, "y": -1}, 'colo_status': "Up", 'colo_last_attack_time': date_start, 'colo_refresh_time': date_start, 'updated': False, 'gift_state': "Not Free"}
                            self.bot.db.push_new_colony(new_colony)   
        date_end: datetime.datetime = datetime.datetime.now()
        print("Infos: players updated", "time :", date_end - date_start)

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
        # print("Infos: task_update_war_infos ended") 
        # print("Infos: task_update_base_status started")
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        obj: dict = {"MB_status": "Down"}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        for player in players:
            date_next: datetime.datetime = player["MB_refresh_time"]
            if now >= date_next:
                if player["MB_status"] == "Down":
                    print("reset")
                    player["MB_status"] = "Back_Up"
                    self.bot.db.update_player(player)
        obj = {"colo_status": "Down"}
        colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
        for colony in colonies:
            date_next: datetime.datetime = colony["colo_refresh_time"]
            if now >= date_next:
                colony["colo_status"] = "Back_Up"
                self.bot.db.update_colony(colony)
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None:
            print(f"Info: Update base status at {date_time_str}")

        # print("Infos: task_update_base_status ended")

        
    #</editor-fold>
    
    #<editor-fold desc="task">

        
    @tasks.loop(minutes=1) #TODO a threader
    async def task_update_war_infos(self):
        # print("Infos: task_update_war_infos started")
        thread_war: Thread = Thread(target=self.thread_task_update_war_infos)
        thread_war.daemon = True
        thread_war.start()
        # thread_war.join()

    # @tasks.loop(minutes=1) #TODO a threader
    # async def task_update_base_status(self):
    #     print("Infos: task_update_base_status started")
    #     t: Thread = Thread(target=self.thread_task_update_base_status)
    #     t.start()
        
    # @tasks.loop(minutes=1) #TODO a threader
    # async def task_update_players_level(self):
        
    #     t: Thread = Thread(target=self.thread_task_update_players_level)
    #     t.start()
    
    # @tasks.loop(minutes=1)
    # async def task_update_reactions(self):
    #     print("Infos: task_update_reactions started")
    #     thread_players: Thread = Thread(target=self.thread_update_players)
    #     thread_players.daemon = True
    #     thread_players.start()
    
    @tasks.loop(minutes=1)
    async def task_update_players(self):
        print("Infos: task_update_players_online started")
        thread_players: Thread = Thread(target=self.thread_update_players)
        print('started for real')
        thread_players.daemon = True
        thread_players.start()
        # thread_players.join()

    @tasks.loop(minutes=1)
    async def task_check_war_status(self):
        print("Infos: task_check_war_status")     
        act_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if act_war is not None and self.war_status == Status.Ended:
            self.war_status = Status.InProgress
            if not self.task_update_war_infos.is_running():
                # print('>>> starting war infos at', datetime.datetime.now())
                self.task_update_war_infos.start()
            if not self.task_update_players.is_running():
                # print('>>> starting update players at', datetime.datetime.now())
                self.task_update_players.start()
        elif self.war_status == Status.InProgress:  
            self.war_status = Status.Ended
            self.task_update_war_infos.stop()
            self.task_update_players.stop()

    #<editor-fold desc="task on ready">

    @task_update_war_infos.before_loop
    async def before_task_update_war_infos(self):
        await self.bot.wait_until_ready()

    # @task_update_players_level.before_loop
    # async def before_task_update_players_level(self):
    #     await self.bot.wait_until_ready()

    @task_update_players.before_loop
    async def before_task_update_players(self):
        await self.bot.wait_until_ready()        
        
    # @task_update_base_status.before_loop
    # async def before_task_update_base_status(self):
    #     await self.bot.wait_until_ready()
        
    @task_check_war_status.before_loop
    async def before_task_check_war_status(self):
        await self.bot.wait_until_ready()

    #</editor-fold>
    
    #</editor-fold>


async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Refresh(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])