import discord
from discord.ext import commands
import datetime
import time
from src.Dropdown import DropView
from models.War_Model import War_Model
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
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
    def create_embed_alliance(war: War_Model, alliance: Alliance_Model) -> discord.Embed:
        embed: discord.Embed
        description: str = f"lvl : {alliance['alliance_lvl'] if alliance['alliance_lvl'] != -1 else 'Non connue'}\n Winrate : {alliance['winrate']} %\n Players : {alliance['player_number']}"
        embed = discord.Embed(title=f"⚔️ {war['alliance_name']} ⚔️️", description=description, color=Colors.purple,timestamp=datetime.datetime.now())
        embed.add_field(name=f"Alliés {war['point']} | {war['enemy_point']} Ennemis",value="")
        return embed

    async def create_Dashboard(self, actual_war: War_Model) -> int:
        thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        dropView: List[discord.ui.View] = []
        if war_alliance is None:
            return -1
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1
        embed: discord.Embed = self.create_embed_alliance(actual_war, war_alliance)
        message = await thread.send(embed=embed)
        infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard"}
        self.bot.db.push_new_info_message(infoMessage)
        for it in range(0, nb_message):
            time.sleep(2.)
            message: discord.abc.Message
            dropView.append(DropView(self.bot, players[(it * 5):(it * 5 + 5)]))
            message = await thread.send(content="­", embed=None, view=dropView[it])
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
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        nb_message: int = len(players) // 5
        if len(players) % 5 > 0:
            nb_message += 1
        embed = self.create_embed_alliance(actual_war, war_alliance)
        obj: dict = {'_id_linked': actual_war["_id"], "type_embed": "Dashboard"}
        infoMessages: List[InfoMessage_Model] = list(self.bot.db.get_info_messages(obj))
        if len(infoMessages) == 0:
            return -1
        message = await thread.fetch_message(int(infoMessages[0]["id_message"]))
        await message.edit(embed=embed)

        for it in range(0, nb_message):
            time.sleep(2.)
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
