import os

import discord
from discord.ext import commands
import datetime
import time
from Utils.Dropdown import DropView
from Models.War_Model import War_Model
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.InfoMessage_Model import InfoMessage_Model
from pymongo.cursor import Cursor
from typing import List
from Models.Colors import Colors
import math

class Dashboard:
    bot: commands.Bot = None
    guild: discord.Guild = None
    ally_alliance_name: str = ""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = self.bot.get_guild(int(os.getenv("SERVER_ID")))
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")

    def create_embed_alliance(self, war: War_Model, alliance: Alliance_Model, players: List[Player_Model]) -> discord.Embed:
        embed: discord.Embed
        title = self.centered_title(war)
        score = self.score_bar(alliance, players)
        war_progress: dict = self.war_progress(alliance["name"], players)
        # # lvl: {alliance['alliance_lvl'] if alliance['alliance_lvl'] != -1 else 'Inconnu'}\n 
        description: str = score["description"]
        winrate: str = f"Winrate: {alliance['alliance_winrate'] if alliance['alliance_winrate'] != -1 else '?'}%­ "
        embed = discord.Embed(title=title, description=description,timestamp=datetime.datetime.now())
        embed.add_field(name=f"{score['title']}",value=f"<:empty:1088454928474841108>\n📈 {winrate}\n💥 Destroyed Planets: {war_progress['total_known_planets']-war_progress['planets_up']}/{war_progress['total_known_planets']}\n🪐 Discovered Colonies: {war_progress['known_colonies']}/{war_progress['total_colonies']}")
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
            filler = filler + "<:empty:1088454928474841108>"
            it += 1
        centered_title = f"{filler}⚔️  {title}  ⚔️"
        
        return centered_title 

    def score_bar(self, alliance: Alliance_Model, players: List[Player_Model]):
        it: int = 1
        return_value: dict = {}
        war_progress: dict = self.war_progress(alliance["name"], players)
        score_space =  (len(str(war_progress['ally_alliance_score'])) - 1 + len(str(war_progress['ennemy_alliance_score']))- 1)
        filler = "<:empty:1088454928474841108>"
        filler_number = 15 - score_space
        while it <= filler_number:
            if len(filler) << 225:
                filler = filler + "<:empty:1088454928474841108>"
            it += 1
        slider: str = ""
        slider_length = 15

        if (war_progress['ally_alliance_score'] + war_progress['ennemy_alliance_score']) != 0:
            slider_score = int(war_progress['ally_alliance_score'] / (war_progress['ally_alliance_score']+ war_progress['ennemy_alliance_score']) * slider_length)
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
        return_value["title"] =  f"💫 {war_progress['ally_alliance_score']}{filler}{war_progress['ennemy_alliance_score']} 💫"
        return_value["description"] = f"{slider}"
        return return_value
        
    async def create_Dashboard(self, actual_war: War_Model) -> int:
        print('create_dashboard')
        thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
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
        embed: discord.Embed = self.create_embed_alliance(actual_war, war_alliance, players)
        message = await thread.send(embed=embed)
        infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard"}
        self.bot.db.push_new_info_message(infoMessage)
        for it in range(0, nb_message):
            time.sleep(1.)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)], actual_war))
            message = await thread.send(content=" ­", embed=None, view=dropView[it])
            infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard;" + str(it)}
            self.bot.db.push_new_info_message(infoMessage)
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
        id_thread = int(actual_war["id_thread"])
        thread = self.guild.get_thread(id_thread)
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        if war_alliance is None:
            return -1  
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        players.sort(key=lambda item: item.get("lvl"), reverse = True)
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1
        embed = self.create_embed_alliance(actual_war, war_alliance, players)
        obj: dict = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard"}
        infoMessages: List[InfoMessage_Model] = list(self.bot.db.get_info_messages(obj))
        if len(infoMessages) == 0:
            return -1
        message = await thread.fetch_message(int(infoMessages[0]["id_message"]))
        await message.edit(embed=embed)
        for it in range(0, nb_message):
            time.sleep(1.)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)], actual_war))
            obj = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard;" + str(it)}
            infoMessages = list(self.bot.db.get_info_messages(obj))
            if len(infoMessages) == 1:
                message = await thread.fetch_message(int(infoMessages[0]["id_message"]))
                await message.edit(content="­", embed=None, view=dropView[it])
            else:
                message = await thread.send(content="­", embed=None, view=dropView[it])
                infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard;" + str(it)}
                self.bot.db.push_new_info_message(infoMessage)
        date_end: datetime.datetime = datetime.datetime.now()
        print("Infos: Dashboard updated", "time :", date_end - date_start)
        return 0

    def war_progress(self, alliance, players):
        return_value: dict = {}
        planets_up: int = 0
        known_colonies: int = 0
        hidden_colonies: int = 0
        main_planet: int = 0
        for player in players:
            main_planet += 1 
            obj: dict = {"_player_id": player["_id"]}
            colonies: List[Colony_Model] = list(self.bot.db.get_colonies(obj))
            if player["MB_status"] == "Up":
                planets_up += 1
            for colo in colonies:
                if colo['colo_coord']['x'] != -1:
                    known_colonies += 1
                    if colo["colo_status"] == "Up":
                        planets_up = planets_up + 1
                else: 
                    hidden_colonies += 1
        return_value["planets_up"] = planets_up
        return_value["known_colonies"] = known_colonies
        return_value["total_colonies"] = known_colonies + hidden_colonies
        return_value["total_known_planets"] = main_planet + known_colonies
        return_value["main_planet"] = main_planet
        
        war_infos: War_Model = self.bot.db.get_one_war("status", "InProgress")
        ennemy_alliance: dict = self.bot.galaxyLifeAPI.get_alliance(alliance)
        ally_alliance: dict = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        if 'ally_initial_score' in war_infos:
            return_value["ally_alliance_score"] = ally_alliance['alliance_score'] - war_infos['ally_initial_score']
            return_value["ennemy_alliance_score"] = ennemy_alliance['alliance_score'] - war_infos['initial_enemy_score']
        else: 
            return_value["ally_alliance_score"] = "x"
            return_value["ennemy_alliance_score"] = "x"
        return return_value