import asyncio
import datetime
import math
import os
import time
from typing import List

import discord
from discord.ext import commands
from pymongo.cursor import Cursor

from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Emoji import Emoji
from Models.InfoMessage_Model import InfoMessage_Model
from Models.Player_Model import Player_Model
from Models.War_Model import War_Model
from Utils.Dropdown import DropView


class Dashboard:
    bot: commands.Bot = None
    guild: discord.Guild = None
    ally_alliance_name: str = ""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = self.bot.get_guild(int(os.getenv("SERVER_ID")))
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")
        self.log_channel_id: int = int(os.getenv("LOG_CHANNEL"))
        self.log_channel = self.bot.get_channel(self.log_channel_id)
        self.log_regen_id: int = int(os.getenv("LOG_REGEN"))
        self.log_regen = self.bot.get_channel(self.log_regen_id)
        self.war_channel_id = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)

    async def create_embed_alliance(self, war: War_Model, alliance: Alliance_Model, players: List[Player_Model], creating: int = 0) -> discord.Embed:
        embed: discord.Embed
        title = self.centered_title(war)
        if creating == 0:
            score = await self.score_bar(alliance, players)
            description: str = score["description"]
            war_progress: dict = await self.war_progress(alliance["name"], players)
        else:
            score = "Loading scores..."
            description = "Loading description..."
            war_progress: dict = {"total_known_planets":"Loading...", "planets_up":"Loading...", "known_colonies":"Loading...", "total_colonies":"Loading...", "instant_score":"Loading...", "score_per_cycle":"Loading..."}
        # # lvl: {alliance['alliance_lvl'] if alliance['alliance_lvl'] != -1 else 'Inconnu'}\n 
        
        if not 'alliance_winrate' in alliance:
            alliance['alliance_winrate'] = 0
        winrate: str = f"Winrate: {alliance['alliance_winrate'] if alliance['alliance_winrate'] != -1 else '?'}%­ "
        embed = discord.Embed(title=title, description=description,timestamp=datetime.datetime.now())
        embed.add_field(name=f"{score['title']}",value=f"{Emoji.empty.value}\n📈 {winrate}\n💥 Destroyed Planets: {war_progress['total_known_planets']-war_progress['planets_up']}/{war_progress['total_known_planets']}\n🪐 Discovered Colonies: {war_progress['known_colonies']}/{war_progress['total_colonies']}\n🎯 Target score: {war_progress['instant_score']}/{war_progress['score_per_cycle']}")
        embed.set_thumbnail(url=alliance["emblem_url"])
        return embed

    @staticmethod
    def centered_title(war):
        title = war['alliance_name'].upper()
        title_space =  len(str(title))
        it: int = 0
        filler = ""
        #largeur = 15 emojis, 25 char
        filler_number_char = (25 - title_space)/2
        filler_number_emojis =  round(filler_number_char * 15 / 25) - 2
        while it <= filler_number_emojis:
            filler = filler + f"{Emoji.empty.value}"
            it += 1
        centered_title = f"{filler}⚔️  {title}  ⚔️"
        
        return centered_title 

    async def score_bar(self, alliance: Alliance_Model, players: List[Player_Model]):
        it: int = 1
        return_value: dict = {}
        war_progress: dict = await self.war_progress(alliance["name"], players)
        score_space =  (len(str(war_progress['ally_alliance_score'])) - 1 + len(str(war_progress['enemy_alliance_score']))- 1)
        filler = f"{Emoji.empty.value}"
        filler_number = 14 - score_space
        while it <= filler_number:
            if len(filler) <= 200:
                filler = filler + f"{Emoji.empty.value}"
            it += 1
        slider: str = ""
        slider_length = 15
        if (war_progress['ally_alliance_score'] + war_progress['enemy_alliance_score']) != 0:
            slider_score = int(war_progress['ally_alliance_score'] / (war_progress['ally_alliance_score']+ war_progress['enemy_alliance_score']) * slider_length)
        else:
            slider_score = 0.5 * slider_length + 1
        it = 0
        while it < slider_score:
            slider = slider + "▰"
            it += 1
        slider = slider + "▰"
        it = 1
        while slider_score + it <= slider_length - 1:
            slider = slider + "▱"
            it += 1
        return_value["title"] =  f"💫 {war_progress['ally_alliance_score']}{filler}{war_progress['enemy_alliance_score']} 💫"
        return_value["description"] = f"{slider}"
        return return_value
        
    async def create_Dashboard(self, actual_war: War_Model) -> int:
        print('creating dashboard')
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        dropView: List[discord.ui.View] = []
        if war_alliance is None:
            return -1
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        players.sort(key=lambda item: item.get("lvl"), reverse = True)
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1   
        embed: discord.Embed = await self.create_embed_alliance(actual_war, war_alliance, players)
        message = await self.war_channel.send(embed=embed)
        await message.add_reaction(f"{Emoji.star.value}")
        await message.add_reaction("🪐")
        infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard"}
        self.bot.db.push_new_info_message(infoMessage)
        for it in range(0, nb_message):
            await asyncio.sleep(.875)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)], actual_war, 1))
            message = await self.war_channel.send(content=" ­", embed=None, view=dropView[it])
            infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard;" + str(it)}
            self.bot.db.push_new_info_message(infoMessage)
        print('dashboard succesfully created')
        return 0
        

    async def update_Dashboard(self) -> int:
        print('update_dashboard')
        date_start: datetime.datetime = datetime.datetime.now()
        embed: discord.Embed
        message: discord.Message
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        dropView: List[discord.ui.View] = []
        if actual_war is None:
            return -1
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        if war_alliance is None:
            return -1  
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        players.sort(key=lambda item: item.get("lvl"), reverse = True)
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1
        embed = await self.create_embed_alliance(actual_war, war_alliance, players)
        obj: dict = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard"}
        infoMessages: List[InfoMessage_Model] = list(self.bot.db.get_info_messages(obj))
        if len(infoMessages) == 0:
            return -1
        message = await self.war_channel.fetch_message(int(infoMessages[0]["id_message"]))
        await message.edit(embed=embed)
        for it in range(0, nb_message):
            await asyncio.sleep(.875)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)], actual_war))
            obj = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard;" + str(it)}
            infoMessages = list(self.bot.db.get_info_messages(obj))
            if len(infoMessages) == 1:
                message = await self.war_channel.fetch_message(int(infoMessages[0]["id_message"]))
                await message.edit(content="­", embed=None, view=dropView[it])
            else:
                message = await self.war_channel.send(content="­", embed=None, view=dropView[it])
                infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard;" + str(it)}
                self.bot.db.push_new_info_message(infoMessage)
        date_end: datetime.datetime = datetime.datetime.now()
        print("Infos: Dashboard updated", "time :", date_end - date_start)
        return 0

    async def war_progress(self, alliance, players):
        time = datetime.datetime.now()
        return_value: dict = {}
        planets_up: int = 0
        known_colonies: int = 0
        hidden_colonies: int = 0
        main_planet: int = 0
        instant_score: int = 0
        dealt_score: int = 0
        score_per_base: list = [100, 200, 300, 500, 600, 1000, 1500, 2000, 2500]
        war_infos: War_Model = self.bot.db.get_one_war("status", "InProgress")
        enemy_alliance: dict = self.bot.galaxyLifeAPI.get_alliance(alliance)
        ally_alliance: dict = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        
        for player in players:
            main_planet += 1 
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            if 'colonies_moved_bool' in player:
                if player['colonies_moved_bool'] == True:
                    await self.log_channel.send(f"> 💢 __Level {player['lvl']}__ **{player['pseudo'].upper()}** has moved a colony !")
                    player['colonies_moved_bool'] = False
            if player["MB_status"] == "Back_Up" or player['war_points_delta'] != 0: #remettre ça dans le thread plus tard en trouvant un moyen d'await la task threadée
                if player["MB_status"] == "Back_Up":
                    await self.log_regen.send(f"> ⬆️ __Level {player['lvl']}__ **{player['pseudo'].upper()}**: 🌍 main base is now back :seedling: `{score_per_base[player['MB_lvl']-1]} pts`")
                    player["MB_status"] = "Up"
                if player['war_points_delta'] != 0:
                    await self.log_channel.send(f">  `☠️ Level {player['lvl']}:` `{player['pseudo']} scored {player['war_points_delta']} points.`")
                    player['war_points_delta'] = 0
                self.bot.db.update_player(player)
            if player["MB_status"] == "Up":
                instant_score += score_per_base[player["MB_lvl"]-1]
                planets_up += 1   
            else:
                dealt_score += score_per_base[player["MB_lvl"]-1] 
            for colo in colonies:
                if colo['colo_coord']['x'] > -1:
                    known_colonies += 1 
                    if colo["colo_status"] == "Back_Up": #remettre ça dans le thread plus tard en trouvant un moyen d'await la task threadée
                        print(colo)
                        await self.log_regen.send(f"> ⬆️ __Level {player['lvl']}__ **{player['pseudo'].upper()}**: 🪐 colony number **{colo['number']} (SB {colo['colo_lvl'] if 'colo_lvl' in colo else 'x'})** is now back :seedling: ``( {colo['colo_coord']['x']} ; {colo['colo_coord']['y']} )`` `{score_per_base[colo['colo_lvl']-1] if 'colo_lvl' in colo else 'x'} pts`")
                        colo["colo_status"] = "Up"
                        self.bot.db.update_colony(colo)
                    if colo["colo_status"] == "Up":
                        planets_up += 1
                        instant_score += score_per_base[colo["colo_lvl"]-1]    
                    else:
                        dealt_score += score_per_base[colo["colo_lvl"]-1] 
                else: 
                    
                    hidden_colonies += 1
            
        score_per_cycle = dealt_score + instant_score
        return_value["planets_up"] = planets_up
        return_value["known_colonies"] = known_colonies
        return_value["total_colonies"] = known_colonies + hidden_colonies
        return_value["total_known_planets"] = main_planet + known_colonies
        return_value["main_planet"] = main_planet
        return_value["instant_score"] = instant_score
        return_value["score_per_cycle"] = score_per_cycle
        

        
        if 'ally_initial_score' in war_infos:
            return_value["ally_alliance_score"] = ally_alliance['alliance_score'] - war_infos['ally_initial_score']
            return_value["enemy_alliance_score"] = enemy_alliance['alliance_score'] - war_infos['initial_enemy_score']
            war_log: dict = self.bot.db.get_warlog()
            if war_log:
                if war_log['enemy_score'][len(war_log['enemy_score'])-1] != return_value['enemy_alliance_score'] or war_log['ally_score'][len(war_log['ally_score'])-1] != return_value['ally_alliance_score']:  
                    war_log['enemy_score'].append(return_value["enemy_alliance_score"])
                    war_log['ally_score'].append(return_value["ally_alliance_score"])
                    war_log['timestamp'].append(time)
                    self.bot.db.update_warlog(war_log)
                    if war_log['enemy_score'][len(war_log['enemy_score'])-2] < war_log['ally_score'][len(war_log['ally_score'])-2] and war_log['enemy_score'][len(war_log['enemy_score'])-1] > war_log['ally_score'][len(war_log['ally_score'])-1]:
                        print('Alert. Beating Us')
                        await self.log_channel.send(f"> ⚠️ Alert : The enemy is beating us !! ⚠️")
            else:
                war_log: dict = {'name': 'warlog', 'enemy_name': alliance, 'enemy_score': [return_value["enemy_alliance_score"]], 'ally_score': [return_value["ally_alliance_score"]], "timestamp": [time]}
                self.bot.db.push_warlog(war_log)
        else: 
            return_value["ally_alliance_score"] = "x"
            return_value["enemy_alliance_score"] = "x"
        return return_value