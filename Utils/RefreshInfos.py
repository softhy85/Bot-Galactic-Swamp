import discord
from discord import app_commands
from datetime import datetime
import discord
from discord import Embed, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext import tasks, commands
from Models.War_Model import War_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.War_Model import War_Model, Status
from pymongo.cursor import Cursor
from typing import List
import os
from Models.Alliance_Model import Alliance_Model
import json


class RefreshInfos(commands.Cog):
    guild: discord.Guild = None
    bot: commands.bot = None
    experiment_channel_id: int = 0
    experiment_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    war_channel_id: int = 0
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    general_channel_id: int = 0
    general_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        self.experiment_channel_id = int(os.getenv("EXPERIMENT_CHANNEL"))
        self.experiment_channel = self.bot.get_channel(self.experiment_channel_id)
        self.war_channel_id  = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.war_channel_id)
        super().__init__()
        self.update_Info_Base.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded : RefreshInfos")

    def cog_unload(self):
        self.update_Info_Base.cancel()

    @tasks.loop(minutes=3)
    async def update_Info_Base(self) -> int:
        now = datetime.now()
        date_time_str = now.strftime("%H:%M:%S")
        print(f"Info: Update at {date_time_str}")
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
        if actual_war is not None:
            await self.bot.dashboard.update_Dashboard()


# async def setup(bot: commands.Bot):
    # guild: discord.Guild = bot.get_guild(int(os.getenv("SERVER_ID")))
    # await bot.add_cog(RefreshInfos(bot=bot, guild=guild), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])