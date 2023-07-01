
import datetime
import os
import re
from datetime import timedelta
from threading import Thread
from typing import List

import discord
from config.definitions import ROOT_DIR
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import utcnow
from Models.Alliance_Model import Alliance_Model
from Models.Next_War_Model import Next_War_Model
from Models.Player_Model import Player_Model
from Models.War_Model import Status, War_Model
from Utils.Utils import Utils


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
        self.utils = Utils(bot)
        self.guild = self.bot.get_guild(int(os.getenv("SERVER_ID")))
        self.app_name: str = os.getenv("APP_NAME")
        self.ally_alliance_name = os.getenv("ALLY_ALLIANCE_NAME")
        self.war_channel_id = int(os.getenv("WAR_CHANNEL"))
        self.war_channel = self.bot.get_channel(self.war_channel_id)
        self.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
        self.general_channel = self.bot.get_channel(self.general_channel_id)
        self.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
        self.command_channel = self.bot.get_channel(self.command_channel_id)
        self.experiment_channel_id = int(os.getenv("EXPERIMENT_CHANNEL"))
        self.experiment_channel = self.bot.get_channel(self.experiment_channel_id)
        self.log_regen_id: int = int(os.getenv("LOG_REGEN"))
        self.log_regen = self.bot.get_channel(self.log_regen_id)
        self.voice_channel_id: int = int(os.getenv("VOICE_CHANNEL"))
        self.voice_channel = self.bot.get_channel(self.voice_channel_id)
        self.war_history_id: int = int(os.getenv("WAR_HISTORY"))
        self.war_history = self.guild.get_thread(self.war_history_id)
        self.program_path: str = os.getenv("PROGRAM_PATH")
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress", self.ally_alliance_name)
        if actual_war is not None:
            self.task_war_over.start()
        else:
            self.task_war_started.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_War")

    #</editor-fold>

    #<editor-fold desc="command">    

    @app_commands.command(name="war_stop", description="stop war")
    @app_commands.describe()
    @app_commands.checks.has_role('Admin')
    async def war_stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress", self.ally_alliance_name)
        date: datetime.datetime = datetime.datetime.now()
        # war_thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
        obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
        players: List[Player_Model] = list(self.bot.db.get_players(obj))
        war_progress = await self.bot.dashboard.war_progress(actual_war["alliance_name"], players)
        converted_start_time = datetime.datetime.strftime(actual_war["start_time"],  "%Y/%m/%d %H:%M:%S.%f")
        strp_converted_start_time = datetime.datetime.strptime(converted_start_time, "%Y/%m/%d %H:%M:%S.%f")
        converted_actual_date = datetime.datetime.strftime(date,  "%Y/%m/%d %H:%M:%S.%f")
        strp_converted_actual_date = datetime.datetime.strptime(converted_actual_date, "%Y/%m/%d %H:%M:%S.%f")
        delta = strp_converted_actual_date - strp_converted_start_time
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        time = hours + minutes / 60 + seconds / 3600
        await interaction.followup.send(f"War has ended")
                                                # after a duration of {hours} hours, {minutes} minutes and {seconds} seconds.\nScore: {war_progress['ally_alliance_score']} VS {war_progress['enemy_alliance_score']}\nTeam members: {api_alliance_GS['alliance_size']} VS {war_progress['main_planet']}")
        if int(war_progress['ally_alliance_score']) and int(war_progress['enemy_alliance_score']) != 0:
            if int(war_progress['ally_alliance_score']) > int(war_progress['enemy_alliance_score']):
                # await war_thread.edit(name=f"{actual_war['alliance_name']} - Won",archived=True, locked=True)
                actual_war["status"] = Status.Win.name
                await self.war_history.send(f"✅ War against {actual_war['alliance_name']} has been won. (**{war_progress['ally_alliance_score']}** vs **{war_progress['enemy_alliance_score']}**)")
            elif int(war_progress['ally_alliance_score']) < int(war_progress['enemy_alliance_score']):
                actual_war["status"] = Status.Lost.name
                # await war_thread.edit(name=f"{actual_war['alliance_name']} - Lost",archived=True, locked=True)
                await self.war_history.send(f"💥 War against {actual_war['alliance_name']} has been lost. (**{war_progress['ally_alliance_score']}** vs **{war_progress['enemy_alliance_score']}**)")
            else:
                actual_war["status"] = Status.Ended.name
                # await war_thread.edit(name=f"{actual_war['alliance_name']} - Over",archived=True, locked=True)
                await self.war_history.send(f"War against {actual_war['alliance_name']} is now over.")
        else:
            actual_war["status"] = Status.Ended.name
            await self.general_channel.send(f"War against {actual_war['alliance_name']} is now over.")
        print(f"Status : {actual_war['status']}")
        self.bot.db.update_war(actual_war)

    #</editor-fold>

    #<editor-fold desc="task">

    @tasks.loop(minutes=1)
    async def task_war_over(self):
        print("Infos: task_war_over started")
        status : Status = Status.Ended
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress", self.ally_alliance_name)
        if actual_war is not None:
            status = await self.update_actual_war()
            # event: discord.ScheduledEvent = await self.guild.fetch_scheduled_events()
            # if event != []:
            #     await event[0].start()
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

    @tasks.loop(minutes=1)
    async def task_war_started(self):
        print("Infos: task_war_started started")
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        alliance_infos = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        if alliance_infos['war_status']:
            await self.set_bot_status(alliance_infos["enemy_name"])
            await self.update_war_channel_name(True)
            await self.create_new_war(alliance_infos["enemy_name"].upper())
            print(f"Info: War started at {date_time_str}")
            self.task_war_started.stop()
            self.task_war_over.start()
        else:
            await self.set_bot_status()
            await self.update_war_channel_name()
            await self.update_peace_embed()
        print("Infos: task_war_started ended")

    @task_war_started.before_loop
    async def before_task_war_started(self):
        await self.bot.wait_until_ready()

    #</editor-fold>

    #<editor-fold desc="other">

    
    async def set_bot_status(self, enemy_name = None):
        
        if enemy_name is not None:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"⚔️ {enemy_name}"), status=discord.Status.dnd)
        else:
            next_war: Next_War_Model = self.bot.db.get_nextwar(self.ally_alliance_name)
            print('next war retrieved:', next_war)
            now = datetime.datetime.now()
            date = datetime.datetime.fromtimestamp(next_war["start_time"])
            now_2 = datetime.datetime.strftime(now, "%d %H %M")
            date_2 = datetime.datetime.strftime(date, "%d %H %M")
            now_3 = datetime.datetime.strptime(now_2, "%d %H %M")
            date_3 = datetime.datetime.strptime(date_2, "%d %H %M")
            next_war_cd = date_3 - now_3
            print(next_war_cd)
            is_day = []
            is_days = []
            is_day.append([m.start() for m in re.finditer('day', str(next_war_cd))])
            is_days.append([m.start() for m in re.finditer('days', str(next_war_cd))])
            if is_day != [] and is_days != [] :
                time_div_list = [' days ', 'h ', ' min' ]
            else:
                time_div_list = [ 'h ', ' min', '' ]
            
            next_war_cleaned_up = str(next_war_cd).replace(' days, ', ':')
            next_war_cleaned_up = str(next_war_cleaned_up).replace(' day, ', ':')
            next_war_cd_list = next_war_cleaned_up.split(":")
            if len(next_war_cd_list) < 3:
                time_div_list = [' min', '' ]
            shield_duration = ""
            print(next_war_cd_list)
            for it in range(0, len(next_war_cd_list)-1):
                if int(next_war_cd_list[it]) > 0:
                    shield_duration = shield_duration + next_war_cd_list[it] + time_div_list[it]
            if shield_duration == "":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"😎 Winning next war"), status=discord.Status.do_not_disturb)
            else:
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"🛡️ {shield_duration}"), status=discord.Status.idle)
        
    
    async def create_new_war(self, alliance: str):
        print('War_Infos: new war')
        self.bot.db.remove_warlog(self.ally_alliance_name)
        print('War_Infos: Warlog has been reset')
        date: datetime.datetime = datetime.datetime.now()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress", self.ally_alliance_name)
        if actual_war is not None:
            await self.command_channel.send(f"We are already at war with {actual_war['alliance_name']}.")
            return
        print('War_Infos: Updating Alliance...')
        act_alliance: Alliance_Model = await self.bot.alliance.update_alliance_war(alliance)
        await self.command_channel.send("> New war started.")
        api_alliance_en = self.bot.galaxyLifeAPI.get_alliance(alliance)
        api_alliance_gs = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        new_message: discord.Message = await (self.war_channel.send(f"<@&1043541214319874058> We are at war against **{act_alliance['name']}** !!"))
        # new_thread: discord.Thread = await new_message.create_thread(name=act_alliance["name"])
        enemy_size: int =  api_alliance_en["alliance_size"]
        ally_size: int =  api_alliance_gs["alliance_size"]
        if enemy_size >= ally_size + 5:
            refresh_duration = 3
        elif enemy_size <= ally_size :
            refresh_duration = 3
        else:
            refresh_duration = 3
        async for message in self.war_channel.history(oldest_first=True):
            await message.delete()
        print(f'Chosen refresh duration: {refresh_duration} hours.')
        new_war: War_Model = {"_alliance_id": act_alliance["_id"], "alliance_name": act_alliance["name"], "initial_enemy_score": api_alliance_en['alliance_score'], "ally_initial_score": api_alliance_gs['alliance_score'], "status": "InProgress", "start_time": date, "refresh_duration": refresh_duration, "ally_name":self.ally_alliance_name}
        print('new war:', new_war)
        new_war["_id"] = self.bot.db.push_new_war(new_war)
        await self.bot.dashboard.create_Dashboard(new_war)
  
    async def set_next_war(self, status: str):
        print('entered set_next_war')
        channel: discord.TextChannel = self.war_channel
        if status == "Win":
            start_time = utcnow() + timedelta(hours=48)
            await self.guild.create_scheduled_event(name='💥 New war', start_time=start_time, channel=self.voice_channel)
        elif status == "Lost":
            start_time = utcnow() + timedelta(hours=72)
            await self.guild.create_scheduled_event(name='💥 New war', start_time=start_time, channel=self.voice_channel)
        else: 
            start_time = utcnow() + timedelta(hours=72)
        next_war: Next_War_Model = {"name": "next_war", "start_time": int(start_time.timestamp()), "negative_votes": 0, "positive_votes": 0, "vote_done": False, "ally_name":self.ally_alliance_name}
        next_war_db: Next_War_Model = self.bot.db.get_nextwar(self.ally_alliance_name)
        print(next_war_db)
        async for message in channel.history(oldest_first=True, limit=10):
            if message.author.name == self.app_name:
                await message.clear_reactions()
                await message.add_reaction("👍🏻")
                await message.add_reaction("👎🏻")
                await message.add_reaction("🪐")
        if next_war_db is None:
            self.bot.db.push_nextwar(next_war)
        else:
            self.bot.db.update_nextwar(next_war)      

    async def update_actual_war(self):
        date: datetime.datetime = datetime.datetime.now()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress", self.ally_alliance_name)
        if actual_war is None:
            await self.command_channel.send("No war actually in progress.")
            return Status.Ended
        else:
            api_alliance_GS = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
            if not api_alliance_GS["war_status"]:
                # war_thread: discord.Thread = self.guild.get_thread(int(actual_war["id_thread"]))
                obj: dict = {"_alliance_id": actual_war["_alliance_id"]}
                players: List[Player_Model] = list(self.bot.db.get_players(obj))
                war_progress = await self.bot.dashboard.war_progress(actual_war["alliance_name"], players)
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
                    time = hours + minutes / 60 + seconds / 3600
                    await self.experiment_channel.send(f"War has ended after a duration of {hours} hours, {minutes} minutes and {seconds} seconds. ({time} h)\nScore: {war_progress['ally_alliance_score']} VS {war_progress['enemy_alliance_score']}\nTeam members: {api_alliance_GS['alliance_size']} VS {war_progress['main_planet']}")
                else:
                    hours = "x"
                    minutes = "x"
                    seconds = "x"
                    await self.experiment_channel.send(f"War has ended after a duration of {hours} hours, {minutes} minutes and {seconds} seconds. Score: {war_progress['ally_alliance_score']} VS {war_progress['enemy_alliance_score']} - Team members: {api_alliance_GS['alliance_size']} VS {war_progress['main_planet']}")
                count: int = 0
                async for message in self.log_regen.history(oldest_first=True):
                    if count != 0:
                        await message.delete()
                    count += 1
                async for message in self.war_channel.history(oldest_first=True):
                    await message.delete()
                if int(war_progress['ally_alliance_score']) and int(war_progress['enemy_alliance_score']) != 0:
                    if int(war_progress['ally_alliance_score']) > int(war_progress['enemy_alliance_score']):
                        actual_war["status"] = Status.Win.name
                        await self.war_history.send(f"✅ War against {actual_war['alliance_name']} has been won. (**{war_progress['ally_alliance_score']}** vs **{war_progress['enemy_alliance_score']}**)")
                    elif int(war_progress['ally_alliance_score']) < int(war_progress['enemy_alliance_score']):
                        actual_war["status"] = Status.Lost.name
                        await self.war_history.send(f"💥 War against {actual_war['alliance_name']} has been lost. (**{war_progress['ally_alliance_score']}** vs **{war_progress['enemy_alliance_score']}**)")
                else:
                    actual_war["status"] = Status.Ended.name
                    await self.general_channel.send(f"War against {actual_war['alliance_name']} is now over.")
                print(f"Status : {actual_war['status']}")
                self.bot.db.update_war(actual_war)
                print('setting next war')
                await self.set_next_war(actual_war['status'])
            return actual_war["status"]

    async def update_war_channel_name(self, active_war: bool = False):
        channel: discord.TextChannel = self.war_channel
        if active_war == True:
            if channel.name != "💥-current-war":
                await channel.edit(name="💥-current-war")
        else:
            if channel.name != "🌌-overview":
                await channel.edit(name="🌌-overview")

    def update_online_players(self):
        alliance_api_info: dict = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name)
        next_war: Next_War_Model = self.bot.db.get_nextwar(self.ally_alliance_name)
        print('next war retrieved:', next_war)
        alliance_players: list = alliance_api_info["members_list"]
        alliance_players.sort(key=lambda item: item.get("WarPoints"), reverse=True)
        online_value: str =  ""
        for player in alliance_players:
            status = self.bot.galaxyLifeAPI.get_player_status(player["Id"])
            if status == 2:
                online_value += "`" + player['Name'] + "` "
        if online_value == "":
            online_value = "_No player is currently online._"
        next_war['players_online_list'] = online_value
        self.bot.db.update_nextwar(next_war)
        
    def create_leaderboard(self):
        return_value = {}
        leaderboard: dict = self.bot.galaxyLifeAPI.get_alliance_leaderboard()
        leaderboard_name: str = f"📈 Current Rank: "
        if "0" in leaderboard and "1" in leaderboard and "2" in leaderboard and "-1" in leaderboard and "-2" in leaderboard: 
            leaderboard_value: str = (f"```ansi\n\u001b[0;0m{leaderboard['3']-2}# ⏫ {leaderboard['-2']['Name']}:    +\u001b[0;31m{leaderboard['-2']['Warpoints']-leaderboard['0']['Warpoints']}\u001b[0;0m"+
                        f"\n{leaderboard['3']-1}# 🔼 {leaderboard['-1']['Name']}:    +\u001b[0;31m{leaderboard['-1']['Warpoints']-leaderboard['0']['Warpoints']}\u001b[0;0m"+
                        f"\n{leaderboard['3']}# ✅ {leaderboard['0']['Name']}:    -------"+
                        f"\n{leaderboard['3']+1}# 🔽 {leaderboard['1']['Name']}:    -\u001b[0;30m{abs(leaderboard['1']['Warpoints']-leaderboard['0']['Warpoints'])}\u001b[0;0m"+
                        f"\n{leaderboard['3']+2}# ⏬ {leaderboard['2']['Name']}:    -\u001b[0;30m{abs(leaderboard['2']['Warpoints']-leaderboard['0']['Warpoints'])}\u001b[0;0m```")
        else:
            leaderboard_value: str = f"```The alliance is under the top 50. Dashboard is deactivated.\nTop 50: ```" #{leaderboard['1']['Name']} : {leaderboard['1']['Warpoints']} 
        return_value["name"] = leaderboard_name
        return_value["value"] = leaderboard_value
        return return_value
    
    def vote_string(self, next_war):
        vote_decay: int = next_war['positive_votes']-next_war['negative_votes']
        if vote_decay <= 4:
            ratio: float = vote_decay/4
        else:
            ratio = 1
        length: int = 25
        progress: int = int(ratio * length)
        it: int = 0
        vote_string: str = ""
        while it <= progress:
            vote_string += "▰"
            it += 1
        while it <= length:
            vote_string += "▱"
            it += 1
        vote_string = "`" + vote_string + "`"
        return vote_string
    
    async def update_peace_embed(self):
        print('Infos: update_peace_embed started')
        channel: discord.TextChannel = self.war_channel
        alliance_api_info: dict = self.bot.galaxyLifeAPI.get_alliance(self.ally_alliance_name) 
        next_war: Next_War_Model = self.bot.db.get_nextwar(self.ally_alliance_name)
        print('next war retrieved:', next_war)
        war_log = self.bot.db.get_warlog(self.ally_alliance_name)  
        leaderboard = self.create_leaderboard()
        if alliance_api_info['alliance_winrate'] != -1:
            alliance_winrate = alliance_api_info['alliance_winrate']
        else:
            alliance_winrate = "xx.xx"
        empty_space_level = self.utils.empty_space("Level:", alliance_api_info['alliance_lvl'], 33)
        empty_space_score = self.utils.empty_space("Score:", alliance_api_info['alliance_formatted_score'], 33)
        empty_space_members = self.utils.empty_space("Members:", str(len(alliance_api_info['members_list'])), 33)
        empty_space_wr = self.utils.empty_space("WR:", str(alliance_winrate), 32)
        alliance_stats = f"```💫 Score:{empty_space_score}{alliance_api_info['alliance_formatted_score']}\n📈 WR:{empty_space_wr}{alliance_api_info['alliance_winrate'] if alliance_api_info['alliance_winrate'] != -1 else 'xx.xx'}% \n⭐ Level:{empty_space_level}{alliance_api_info['alliance_lvl']}\n👤 Members:{empty_space_members}{len(alliance_api_info['members_list'])}```"
        embed_title: str = ""
        war_start_string = f"➡️ Next war <t:{int(next_war['start_time'])}:R>"
        
        war_recap = discord.File(f"{os.path.join(ROOT_DIR, 'Image', 'war_recap.png')}", filename="war_recap.png")
        
        if next_war['positive_votes'] > 0 and (next_war['positive_votes'] - next_war['negative_votes']) < 4:
            war_start_string = f"➡️ Next war <t:{int(next_war['start_time'])}:R> `({4-next_war['positive_votes']+next_war['negative_votes']} votes to start)`"
            vote_string = self.vote_string(next_war)
        elif next_war['positive_votes'] - next_war['negative_votes'] > 3 and next_war['vote_done'] == False:
            war_start_string = "✅ The team has voted. A war will start soon."
            vote_string = self.vote_string(next_war)
            await self.general_channel.send('<@&1043539666479099974> **time to start a war !!!**')
            next_war['vote_done'] = True
            self.bot.db.update_nextwar(next_war)
        elif next_war['positive_votes'] - next_war['negative_votes'] > 3 and next_war['vote_done'] == True:
            war_start_string = "✅ The team has voted. A war will start soon."
            vote_string = self.vote_string(next_war)
        else:
            vote_string = f"Vote to get the war faster (ceil: 4 votes)"
        updated: bool = False
        t: Thread = Thread(target=self.update_online_players)
        t.start()
        async for message in channel.history(oldest_first=True, limit=10):
            if message.author.name == self.app_name:
                updated = True
        embed = discord.Embed(title=embed_title, description="",timestamp=datetime.datetime.now())
        embed.add_field(name="🎯 Alliance stats:", value=alliance_stats)
        embed.add_field(name=leaderboard['name'], value=leaderboard['value'], inline=False)
        embed.add_field(name="⛔ Players online:", value=next_war['players_online_list'], inline=False)
        embed.add_field(name=war_start_string, value=vote_string, inline=False)
        if war_log is not None:
            embed.add_field(name=f"💥 Last war recap: `{war_log['enemy_name']}`", value=f"``{war_log['ally_score'][-1]}`` vs ``{war_log['enemy_score'][-1]}`` - ``{len(war_log['ally_score'])} attacks`` - ``{'Win' if war_log['ally_score'][-1] >war_log['enemy_score'][-1] else 'Lost'}``", inline=False)
        banner = discord.File(f"{os.path.join(ROOT_DIR, 'Image', 'banner.png')}", filename="banner.png")
        embed.set_image(url="attachment://war_recap.png")
        if updated == False:
            self.bot.galaxyCanvas.draw_recap()
            message = await channel.send(embed=embed, files=[war_recap, banner])
            await message.add_reaction("👍🏻")
            await message.add_reaction("👎🏻")
            await message.add_reaction("🪐")
        else:
            self.bot.galaxyCanvas.draw_recap()
            await message.edit(embed=embed)  
        print('Infos: update_peace_embed ended')
        
    #</editor-fold>
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_War(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])