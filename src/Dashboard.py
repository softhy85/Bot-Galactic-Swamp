import discord
from discord.ext import commands
import datetime
import time
from src.Dropdown import DropView
from models.War_Model import War_Model
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from models.InfoMessage_Model import InfoMessage_Model
from pymongo.cursor import Cursor
from typing import List
from models.Colors import Colors

class Dashboard:
    bot: commands.Bot
    guild: discord.Guild
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild

    @staticmethod
    def create_embed_alliance(self, war: War_Model, alliance: Alliance_Model, players: List[Player_Model]) -> discord.Embed:
        embed: discord.Embed
        war_progress: dict = self.war_progress(alliance["name"], players)
        description: str = f"lvl: {alliance['alliance_lvl'] if alliance['alliance_lvl'] != -1 else 'Inconnu'}\n Winrate: {alliance['alliance_winrate'] if alliance['alliance_winrate'] != -1 else '❔'}%\n­ "
        embed = discord.Embed(title=f"⚔️ {war['alliance_name'].upper()} ⚔️️", description=description, color=Colors.purple,timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=alliance["emblem_url"])
        embed.add_field(name=f"Alliés 💫 {war_progress['ally_alliance_score']} | {war_progress['ennemy_alliance_score']} 💫 Ennemis\n",value=f"\n­ \n💥 Planètes détruites: {war_progress['total_known_planets']-war_progress['planets_up']}/{war_progress['total_known_planets']}\n🪐Colonies découvertes: {war_progress['known_colonies']}/{war_progress['total_colonies']}")
        return embed

    async def create_Dashboard(self, actual_war: War_Model) -> int:
        thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        dropView: List[discord.ui.View] = []
        if war_alliance is None:
            return -1
        alliance_info = self.bot.galaxylifeapi.get_alliance(war_alliance["name"])
        if alliance_info != None:
            war_alliance["alliance_lvl"] = alliance_info["alliance_lvl"]
            war_alliance["alliance_winrate"] = alliance_info["alliance_winrate"]
            war_alliance["emblem_url"] = alliance_info["emblem_url"]
        else:
            war_alliance["alliance_lvl"] = 0
            war_alliance["alliance_winrate"] = "x"
            war_alliance["emblem_url"] = ""
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        for it in range(0, len(players)):
            player_temp: dict = self.bot.galaxylifeapi.get_player_infos(players[it]["id_gl"])
            players[it]["player_lvl"] = player_temp["player_lvl"]
        players.sort(key=lambda item: item.get("player_lvl"), reverse = True)
        for it in range(0, len(players)):
            if "id_gl" in players[it]:
                players[it]["player_online"] = self.bot.galaxylifeapi.get_player_status(players[it]['id_gl'])
            else:
                players[it]["player_online"] = 0
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1
        embed: discord.Embed = self.create_embed_alliance(self, actual_war, war_alliance, players)
        message = await thread.send(embed=embed)
        infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard"}
        self.bot.db.push_new_info_message(infoMessage)
        for it in range(0, nb_message):
            time.sleep(1.)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)]))
            message = await thread.send(content=" ­", embed=None, view=dropView[it])
            infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard;" + str(it)}
            self.bot.db.push_new_info_message(infoMessage)
        return 0

    async def update_Dashboard(self) -> int:
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
        alliance_info = self.bot.galaxylifeapi.get_alliance(war_alliance["name"])
        if alliance_info != None:
            war_alliance["alliance_lvl"] = alliance_info["alliance_lvl"]
            war_alliance["alliance_winrate"] = alliance_info["alliance_winrate"]
            war_alliance["emblem_url"] = alliance_info["emblem_url"]
        else:
            war_alliance["alliance_lvl"] = 0
            war_alliance["alliance_winrate"] = "x"
            war_alliance["emblem_url"] = ""
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        for it in range(0, len(players)):
            player_temp: dict = self.bot.galaxylifeapi.get_player_infos(players[it]["id_gl"])
            players[it]["player_lvl"] = player_temp["player_lvl"]
        players.sort(key=lambda item: item.get("player_lvl"), reverse = True)
        for it in range(0, len(players)):
            if "id_gl" in players[it]:
                players[it]["player_online"] = self.bot.galaxylifeapi.get_player_status(players[it]['id_gl'])
                #if players[it]["player_online"] == 1:
                  #  print('player online')
                #else:
                  #  print('player offline')
            else:
                players[it]["player_online"] = 0
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1
        embed = self.create_embed_alliance(self, actual_war, war_alliance, players)
        obj: dict = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard"}
        infoMessages: List[InfoMessage_Model] = list(self.bot.db.get_info_messages(obj))
        if len(infoMessages) == 0:
            return -1
        message = await thread.fetch_message(int(infoMessages[0]["id_message"]))
        await message.edit(embed=embed)

        for it in range(0, nb_message):
            time.sleep(1.)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)]))
            obj = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard;" + str(it)}
            infoMessages = list(self.bot.db.get_info_messages(obj))
            if len(infoMessages) == 1:
                message = await thread.fetch_message(int(infoMessages[0]["id_message"]))
                await message.edit(content="­", embed=None, view=dropView[it])
            else:
                message = await thread.send(content="­", embed=None, view=dropView[it])
                infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard;" + str(it)}
                self.bot.db.push_new_info_message(infoMessage)
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
                if colo['colo_coord']['x'] != "-1":
                    known_colonies += 1
                    if colo["colo_status"] == "Up":
                        planets_up = planets_up + 1
                else: 
                    hidden_colonies += 1
        return_value["planets_up"] = planets_up
        return_value["known_colonies"] = known_colonies
        return_value["total_colonies"] = known_colonies + hidden_colonies
        return_value["total_known_planets"] = main_planet + known_colonies
        
        war_infos: War_Model = self.bot.db.get_one_war("status", "InProgress")
        ally_alliance_name: str = "GALACTIC SWAMP"
        ennemy_alliance: dict = self.bot.galaxylifeapi.get_alliance(alliance)
        ally_alliance: dict = self.bot.galaxylifeapi.get_alliance(ally_alliance_name)
        if 'ally_initial_score' in war_infos:
            return_value["ally_alliance_score"] = ally_alliance['alliance_score'] - war_infos['ally_initial_score']
            return_value["ennemy_alliance_score"] = ennemy_alliance['alliance_score'] - war_infos['initial_enemy_score']
        else: 
            return_value["ally_alliance_score"] = "x"
            return_value["ennemy_alliance_score"] = "x"
        return return_value
    
