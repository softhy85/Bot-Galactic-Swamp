import discord
from discord import app_commands
import datetime
from discord.ext import tasks, commands
from models.War_Model import War_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from pymongo.cursor import Cursor
from typing import List
import os


class Refresh_Infos(commands.Cog):
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_Info_Base.start()
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Refresh_Infos cog loaded.")

    def cog_unload(self):
        self.update_Info_Base.cancel()

    @tasks.loop(minutes=10.0)
    async def update_Info_Base(self) -> int:
        obj: dict = {"MB_status": "Down"}
        players: Cursor[Player_Model] = self.bot.db.get_players(obj)
        for player in players:
            date: datetime.datetime = datetime.datetime.now()
            date_next: datetime.datetime = player["MB_refresh_time"]
            if date > date_next:
                player["MB_status"] = "Up"
                self.bot.db.update_player(player)
        obj = {"colo_status": "Down"}
        colonies: Cursor[Colony_Model] = self.bot.db.get_colonies(obj)
        for colony in colonies:
            date: datetime.datetime = datetime.datetime.now()
            date_next: datetime.datetime = colony["colo_refresh_time"]
            if date > date_next:
                colony["colo_status"] = "Up"
                self.bot.db.update_colony(colony)
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            await self.bot.dashboard.update_Dashboard()

async def setup(bot: commands.Bot):
    await bot.add_cog(Refresh_Infos(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])