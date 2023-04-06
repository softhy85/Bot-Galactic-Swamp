import discord
from discord import Embed, app_commands
from discord.ext import commands
from Models.Alliance_Model import Alliance_Model
from Models.War_Model import War_Model, Status
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from discord.ext import tasks, commands
from typing import List
import os
import datetime
import re
import time

class Cog_War(commands.Cog):
    bot: commands.Bot = None
    guild: discord.Guild = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    general_channel_id: int = None
    general_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    command_channel_id: int = None
    command_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    experiment_channel_id: int = None
    experiment_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
    ally_alliance_name: str = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.guild: discord.Guild = self.bot.get_guild(int(os.getenv("SERVER_ID")))
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")
        self.war_channel_id = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.war_channel_id)
        self.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
        self.command_channel = self.bot.get_channel(self.command_channel_id)
        self.experiment_channel_id = int(os.getenv("EXPERIMENT_CHANNEL"))
        self.experiment_channel = self.bot.get_channel(self.experiment_channel_id)
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            self.task_war_over.start()
        else:
            self.task_war_started.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_War")

    #</editor-fold>

    #<editor-fold desc="autocomplete">

    async def alliance_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        obj: dict = {}
        if current != "":
            obj: dict = {"name": {"$regex": re.compile(current, re.IGNORECASE)}}
        alliances: List[Alliance_Model] = list(self.bot.db.get_alliances(obj))
        alliances = alliances[0:25]
        return [
            app_commands.Choice(name=alliance["name"], value=alliance["name"])
            for alliance in alliances
        ]

    #</editor-fold>

    #<editor-fold desc="command">

    @app_commands.command(name="war_new", description="Start a new war")
    @app_commands.describe(alliance="The name of the alliance against which you are at war")
    @app_commands.autocomplete(alliance=alliance_autocomplete)
    @app_commands.checks.has_role('Admin')
    @app_commands.default_permissions()
    async def war_new(self, interaction: discord.Interaction, alliance: str):
        date: datetime.datetime = datetime.datetime.now()
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        if alliance.strip() == "":
            await interaction.response.send_message(f"Cannot create alliances with a name composed only of whitespace.")
            return
        interaction.response.send_message("Loading the new war.")
        await self.create_new_war(alliance)

    @app_commands.command(name="war_update", description="Check and update the current war")
    @app_commands.describe()
    @app_commands.checks.has_role('Admin')
    async def war_update(self, interaction: discord.Interaction):
        if not self.bot.spec_role.admin_role(interaction.guild, interaction.user):
            await interaction.response.send_message("You don't have the permission to use this command.")
            return
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        print("Infos: command war_update started")
        if actual_war is None:
            await interaction.response.send_message("No war actually in progress.")
        else:
            await interaction.response.send_message("Updating the current war")
            await self.bot.alliance.update_alliance(actual_war["alliance_name"])
            await self.update_actual_war()
        print("Infos: command war_update ended")

    #</editor-fold>

    #<editor-fold desc="task">

    @tasks.loop(minutes=5)
    async def task_war_over(self):
        print("Infos: task_war_over started")
        status : Status = Status.Ended
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            status = await self.update_actual_war()
        if status != Status.InProgress.name:
            print(f"Info: War is over at {date_time_str}")
            self.task_war_over.stop()
            self.task_war_started.start()
        else: 
            await self.bot.dashboard.update_Dashboard()
        print("Infos: task_war_over ended")

    @task_war_over.before_loop
    async def before_task_war_over(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def task_war_started(self):
        print("Infos: task_war_started started")
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        alliance_infos = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        if alliance_infos['war_status']:
            await self.create_new_war(alliance_infos["enemy_name"].upper())
            print(f"Info: War started at {date_time_str}")
            self.task_war_started.stop()
            self.task_war_over.start()
        print("Infos: task_war_started ended")

    @task_war_started.before_loop
    async def before_task_war_started(self):
        await self.bot.wait_until_ready()

    #</editor-fold>

    #<editor-fold desc="other">

    async def create_new_war(self, alliance: str):
        date: datetime.datetime = datetime.datetime.now()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is not None:
            await self.command_channel.send(f"We are already at war with {actual_war['alliance_name']}.")
            return
        act_alliance: Alliance_Model = await self.bot.alliance.update_alliance(alliance)
        await self.command_channel.send("> New war started.")
        api_alliance_en = self.bot.galaxyLifeAPI.get_alliance(alliance)
        api_alliance_gs = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        new_message: discord.Message = await (self.war_channel.send(f"<@&1043541214319874058> We are at war against **{act_alliance['name']}** !!"))
        new_thread: discord.Thread = await new_message.create_thread(name=act_alliance["name"])
        new_war: War_Model = {"_alliance_id": act_alliance["_id"], "alliance_name": act_alliance["name"], "id_thread": new_thread.id, "initial_enemy_score": api_alliance_en['alliance_score'], "ally_initial_score": api_alliance_gs['alliance_score'], "status": "InProgress", "start_time": date}
        new_war["_id"] = self.bot.db.push_new_war(new_war)
        await self.bot.dashboard.create_Dashboard(new_war)

    async def update_actual_war(self):
        date: datetime.datetime = datetime.datetime.now()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        if actual_war is None:
            await self.command_channel.send("No war actually in progress.")
            return Status.Ended
        else:
            api_alliance_GS = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
            # print('stop')
            # time.Sleep(10)
            if not api_alliance_GS["war_status"]:
                war_thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
                obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
                players: List[Player_Model] = list(self.bot.db.get_players(obj))
                war_progress = self.bot.dashboard.war_progress(actual_war["alliance_name"], players)
                if "start_time" in actual_war:
                    converted_start_time = datetime.datetime.strftime(actual_war["start_time"],  "%Y/%m/%d %H:%M:%S.%f")
                    strp_converted_start_time = datetime.datetime.strptime(converted_start_time, "%Y/%m/%d %H:%M:%S.%f")
                    converted_actual_date = datetime.datetime.strftime(date,  "%Y/%m/%d %H:%M:%S.%f")
                    strp_converted_actual_date = datetime.datetime.strptime(converted_actual_date, "%Y/%m/%d %H:%M:%S.%f")
                    delta = strp_converted_actual_date - strp_converted_start_time
                    days, seconds = delta.days, delta.seconds
                    hours = days * 24 + seconds // 3600
                    minutes = (seconds % 3600) // 60
                    seconds = seconds % 60
                    await self.experiment_channel.send(f"War has ended after a duration of {hours} hours, {minutes} minutes and {seconds} seconds. Score: {war_progress['ally_alliance_score']} VS {war_progress['ennemy_alliance_score']} - Team members: {api_alliance_GS['alliance_size']} VS {war_progress['main_planet']}")
                else:
                    hours = "x"
                    minutes = "x"
                    seconds = "x"
                    await self.experiment_channel.send(f"War has ended after a duration of {hours} hours, {minutes} minutes and {seconds} seconds. Score: {war_progress['ally_alliance_score']} VS {war_progress['ennemy_alliance_score']} - Team members: {api_alliance_GS['alliance_size']} VS {war_progress['main_planet']}")

                if war_thread is not None:
                    if int(war_progress['ally_alliance_score']) and int(war_progress['ennemy_alliance_score']) != 0:
                        if int(war_progress['ally_alliance_score']) > int(war_progress['ennemy_alliance_score']):
                            await war_thread.edit(name=f"{actual_war['alliance_name']} - Won",archived=True, locked=True)
                            actual_war["status"] = Status.Win.name
                            await self.general_channel.send(f"War against {actual_war['alliance_name']} has been won.")
                        elif int(war_progress['ally_alliance_score']) < int(war_progress['ennemy_alliance_score']):
                            actual_war["status"] = Status.Lost.name
                            await war_thread.edit(name=f"{actual_war['alliance_name']} - Lost",archived=True, locked=True)
                            await self.general_channel.send(f"War against {actual_war['alliance_name']} has been lost.")
                    else:
                        actual_war["status"] = Status.Ended.name
                        await war_thread.edit(name=f"{actual_war['alliance_name']} - Over",archived=True, locked=True)
                        await self.general_channel.send(f"War against {actual_war['alliance_name']} is now over.")
                else:
                    actual_war["status"] = Status.Ended.name
                    await self.general_channel.send(f"War against {actual_war['alliance_name']} is now over.")
                print(f"Status : {actual_war['status']}")
                self.bot.db.update_war(actual_war)
            return actual_war["status"]

    #</editor-fold>


async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_War(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])