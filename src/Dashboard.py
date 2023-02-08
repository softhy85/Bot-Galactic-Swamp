import discord
from discord.ext import commands
import datetime
from src.Dropdown import DropView
from models.War_Model import War_Model
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
from models.InfoMessage_Model import InfoMessage_Model
from pymongo.cursor import Cursor


class Dashboard:
    bot: commands.Bot
    guild: discord.Guild
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild

    @staticmethod
    def create_embed_alliance(war: War_Model, alliance: Alliance_Model) -> discord.Embed:
        embed: discord.Embed
        description: str = f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\nlvl : {alliance['alliance_lvl']}"
        embed = discord.Embed(title=f"💣 {war['alliance_name']} 💣", description=description, color=0x310c31,timestamp=datetime.datetime.now())
        embed.add_field(name=f"Alliés {war['point']} | {war['enemy_point']} Ennemis", value="")
        return embed

    async def create_Dashboard(self, actual_war: War_Model) -> int:
        embed: discord.Embed
        thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        if war_alliance is None:
            return -1
        obj: dict = {"_alliance_id", actual_war["_alliance_id"]}
        players: Cursor[Player_Model] = self.bot.db.get_players(obj)
        embed = self.create_embed_alliance(actual_war, war_alliance)
        dropView = DropView(self.bot, players)
        message: discord.abc.Message = await thread.send(embed=embed, view=dropView)
        infoMessage: InfoMessage_Model = {"_id_linked": actual_war["_id"], "id_message": message.id, "type_embed": "Dashboard"}
        self.bot.db.push_new_info_message(infoMessage)
        return 0

    async def update_Dashboard(self) -> int:
        embed: discord.Embed
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is None:
            return -1
        id_thread = int(actual_war["id_thread"])
        thread = self.guild.get_thread(id_thread)
        war_alliance: Alliance_Model = self.bot.db.get_one_alliance("_id", actual_war["_alliance_id"])
        if war_alliance is None:
            return -1
        obj: dict = {"_alliance_id", actual_war["_alliance_id"]}
        players: Cursor[Player_Model] = self.bot.db.get_players(obj)
        embed = self.create_embed_alliance(actual_war, war_alliance)
        dropView = DropView(self.bot, players)
        infoMessage: InfoMessage_Model = self.bot.db.get_one_info_message('_id_linked', actual_war["_id"])
        message: discord.Message = await thread.fetch_message(int(infoMessage["id_message"]))
        await message.edit(embed=embed, view=dropView)
        return 0