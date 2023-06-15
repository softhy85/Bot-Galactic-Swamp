import datetime
import os
from typing import List

import discord
from discord import Client, app_commands
from discord.ext import commands, tasks
from Models.War_Model import War_Model
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model

class Cog_Tasks(commands.Cog):
    bot: commands.Bot = None
    war_channel_id: int = None
    war_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.client = discord.Client
        self.log_channel_id = int(os.getenv("LOG_CHANNEL"))
        self.log_channel = bot.get_channel(bot.log_channel_id)
        self.app_name = os.getenv("APP_NAME")

        if not self.check_if_war.is_running():
            self.check_if_war.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Tasks")

    #</editor-fold>

    async def task_update_leaked_colonies(self):
        print('beginning')
        reaction_list = ['1_', '2_', '3_', '4_', '5_', "6_", "7_", "8_", "9_", "10_", "11_"]
        date = datetime.datetime.now()
        leaked_colonies = self.bot.db.get_leaked_colonies()
        if not leaked_colonies:
           leaked_colonies = self.bot.db.create_leaked_colonies()  
        previous_last_update =  leaked_colonies["last_update"] 
        print('0.1')
        history = [message async for message in self.bot.log_channel.history(before=date, after=leaked_colonies["last_update"], limit=2)]
        print('0.2')
        for message in history:
            username = message.content.split('**')[1]
            if message.author.name == self.app_name:
                print('.03')
                for index in range(0, len(message.reactions)):
                    users = [user async for user in message.reactions[index].users()]
                    for user in users:
                        print('0.41')
                        if user != message.author:
                            for emoji_index in range(0, len(reaction_list)):
                                emoji = message.reactions[index].emoji.name
                                if emoji == reaction_list[emoji_index]:
                                    emoji = str(emoji_index+1)
                                    break
                                else:
                                    emoji = "0"
                            if user.name in leaked_colonies:
                                if not username in leaked_colonies[user.name]:
                                    leaked_colonies[user.name][username] = []
                                if not emoji in leaked_colonies[user.name][username]:
                                    leaked_colonies[user.name][username].append(emoji)
                            else: 
                                leaked_colonies[user.name] = {}
                                leaked_colonies[user.name][username] = []
                                leaked_colonies[user.name][username].append(emoji)
        print('0.5')
        end_date = datetime.datetime.now()
        leaked_colonies["last_update"] = end_date
        self.bot.db.update_leaked_colonies(leaked_colonies)
        content = {}
        alliance: Alliance_Model = self.bot.db.get_one_alliance('name', "KORNAD CLAN")
        players_list: List(Player_Model) = list(self.bot.db.get_players_from_alliance(alliance["_id"]))
        for index_player in leaked_colonies:
            if index_player != 'last_update' and index_player != 'registered_users':
                content[index_player] = ""
                for enemy in leaked_colonies[f'{index_player}']:
                    it_player = 0
                    player_data = None
                    for player in players_list:
                        if player['pseudo'].upper() == enemy:
                            player_data = it_player
                        it_player += 1
                    if len(leaked_colonies[f'{index_player}'][enemy]) > 0:
                        prefix_string = "```py\n"
                        suffix_string = "```"
                        if player_data is not None:
                            if 'state' in players_list[player_data]:
                                if players_list[player_data]['state'] == "leaker":
                                    prefix_string = "```ansi\n\u001b[0;31m"
                        content[index_player] = content[index_player] + f"{prefix_string}{enemy}: "
                        for colony in leaked_colonies[f'{index_player}'][f'{enemy}']:
                            content[index_player] = content[index_player] + f"{colony} "
                        content[index_player] = content[index_player] + f"{suffix_string}" 
                if content[index_player] == f"\n**{index_player}**:":
                    content[index_player] = ""
       
        print('before that')
        for user_id in leaked_colonies['registered_users']:
            bot_msg_list = []
            user_dm=await self.bot.fetch_user(int(user_id))
            if user_dm.name in content:
                if content[user_dm.name] != "":
                    embed: discord.Embed = discord.Embed(title=f"🔎 Leaked Colonies", description=content[user_dm.name], color=discord.Color.from_rgb(8, 1, 31), timestamp=date)
                    print('1')
                    if user_dm.dm_channel is not None:
                        channel = user_dm.dm_channel
                    else:
                        channel = await user_dm.create_dm()
                    dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                    for message in dm_history:
                        if str(message.author.name) == str(self.app_name):
                            bot_msg_list.append(message)
                    if len(dm_history) == 0 or bot_msg_list == []:
                        message = await channel.send('Loading...')
                        bot_msg_list.append(message)
                    for msg_index in range(0, len(bot_msg_list)):
                        if msg_index < len(bot_msg_list)-1:
                            await bot_msg_list[msg_index].delete()
                        else:
                            await bot_msg_list[msg_index].edit(embed=embed, content="")
                    print('4')
                else:
                    if user_dm.dm_channel is not None:
                        channel = user_dm.dm_channel
                    else:
                        channel = await user_dm.create_dm()
                    dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                    for message in dm_history:
                        if str(message.author.name) == str(self.app_name):
                            bot_msg_list.append(message)
                    if len(dm_history) == 0 or bot_msg_list == []:
                        message = await channel.send('Loading...')
                        bot_msg_list.append(message)
                    for msg_index in range(0, len(bot_msg_list)):
                        if msg_index < len(bot_msg_list)-1:
                            await bot_msg_list[msg_index].delete()
                        else:
                            await bot_msg_list[msg_index].edit(content="Your colonies are currently kept secret", embed=None)
            else:
                if user_dm.dm_channel is not None:
                    channel = user_dm.dm_channel
                else:
                    channel = await user_dm.create_dm()
                dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                for message in dm_history:
                    if str(message.author.name) == str(self.app_name):
                        bot_msg_list.append(message)
                if len(dm_history) == 0 or bot_msg_list == []:
                    message = await channel.send('Loading...')
                    bot_msg_list.append(message)
                for msg_index in range(0, len(bot_msg_list)):
                    if msg_index < len(bot_msg_list)-1:
                        await bot_msg_list[msg_index].delete()
                    else:
                        await bot_msg_list[msg_index].edit(content="Your colonies are currently kept secret", embed=None)
        print('before', leaked_colonies["last_update"], 'after', previous_last_update),  #- datetime.timedelta(seconds=20)
        history = [message async for message in self.log_channel.history(before=leaked_colonies["last_update"] , after=previous_last_update, limit=2)] #before=date - datetime.timedelta(seconds=20),
        for message in history:
            for index in range(0, len(message.reactions)):
                await message.remove_reaction(emoji=message.reactions[index], member=message.author)
    
    async def clean_leaked_colonies(self):
        leaked_colonies = self.bot.db.get_leaked_colonies()
        if not leaked_colonies:
           leaked_colonies = self.bot.db.create_leaked_colonies()  
        leaked_colonies_updated = {'last_update': leaked_colonies['last_update'], 'registered_users': leaked_colonies['registered_users']}
        for user_id in leaked_colonies['registered_users']:
            user_dm=await self.bot.fetch_user(int(user_id))
            if user_dm.dm_channel is not None:
                channel = user_dm.dm_channel
                dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                if len(dm_history) > 0: 
                    for msg_index in range(0, len(dm_history)):
                        if dm_history[msg_index].author.name == self.app_name:
                            await dm_history[msg_index].delete()     
        self.bot.db.update_leaked_colonies(leaked_colonies_updated)
        
    @tasks.loop(minutes=1)
    async def check_if_war(self):
        print("Infos: check_if_war started")
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        leaked_colonies = self.bot.db.get_leaked_colonies()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
        print('actual war:', actual_war)
        if actual_war is not None:
            await self.task_update_leaked_colonies()
        elif len(leaked_colonies) > 2:
            await self.task_update_leaked_colonies()
            await self.clean_leaked_colonies()
        print("Infos: check_if_war ended")

    @check_if_war.before_loop
    async def before_check_if_war(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Tasks(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])