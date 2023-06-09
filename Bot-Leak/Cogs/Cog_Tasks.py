import discord
from discord import app_commands, Client
from discord.ext import commands, tasks
from typing import List
import datetime
import os
from Models.War_Model import War_Model

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
        
        if not self.check_if_war.is_running():
            self.check_if_war.start()

    #<editor-fold desc="listener">

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Loaded: Cog_Tasks")

    #</editor-fold>

    async def task_update_leaked_colonies(self):
        reaction_list = ['1_', '2_', '3_', '4_', '5_', "6_", "7_", "8_", "9_", "10_", "11_"]
        date = datetime.datetime.now()
        leaked_colonies = self.bot.db.get_leaked_colonies()
        if not leaked_colonies:
           leaked_colonies = self.bot.db.create_leaked_colonies()  
        previous_last_update =  leaked_colonies["last_update"] 
        history = [message async for message in self.bot.log_channel.history(before=date, after=leaked_colonies["last_update"])]
        for message in history:
            username = message.content.split('**')[1]
            if message.author.name == "Galactic-Swamp-app":
                for index in range(0, len(message.reactions)):
                    users = [user async for user in message.reactions[index].users()]
                    for user in users:
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
        end_date = datetime.datetime.now()
        leaked_colonies["last_update"] = end_date
        self.bot.db.update_leaked_colonies(leaked_colonies)
        content = {}
        for index_player in leaked_colonies:
            if index_player != 'last_update' and index_player != 'registered_users':
                content[index_player] = ""
                content[index_player] = content[index_player] + f"\n**{index_player}**:"
                for enemy in leaked_colonies[f'{index_player}']:
                    if len(leaked_colonies[f'{index_player}'][enemy]) > 0:
                        content[index_player] = content[index_player] + f"```py\n{enemy}: "
                        for colony in leaked_colonies[f'{index_player}'][f'{enemy}']:
                            content[index_player] = content[index_player] + f"{colony} "
                        content[index_player] = content[index_player] + "```" 
                if content[index_player] == f"\n**{index_player}**:":
                    content[index_player] = ""
        for user_id in leaked_colonies['registered_users']:
            user_dm=await self.bot.fetch_user(int(user_id))
            if user_dm.name in content:
                if content[user_dm.name] != "":
                    embed: discord.Embed = discord.Embed(title=f"Leaked Colonies", description=content[user_dm.name], color=discord.Color.from_rgb(8, 1, 31), timestamp=date)
                    if user_dm.dm_channel is not None:
                        channel = user_dm.dm_channel
                    else:
                        channel = await user_dm.create_dm()
                    dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                    if len(dm_history) == 0:
                        await channel.send('Loading...')
                    for msg_index in range(0, len(dm_history)):
                        if msg_index < len(dm_history)-1:
                            await dm_history[msg_index].delete()
                        else:
                            await dm_history[msg_index].edit(embed=embed, content="")
                else:
                    
                    if user_dm.dm_channel is not None:
                        channel = user_dm.dm_channel
                    else:
                        channel = await user_dm.create_dm()
                    dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                    if len(dm_history) == 0:
                        await channel.send('Loading...')
                    for msg_index in range(0, len(dm_history)):
                        if msg_index < len(dm_history)-1:
                            await dm_history[msg_index].delete()
                        else:
                            await dm_history[msg_index].edit(content="Your colonies are currently kept secret", embed=None)
            else:
                if user_dm.dm_channel is not None:
                    channel = user_dm.dm_channel
                else:
                    channel = await user_dm.create_dm()
                dm_history = [msg async for msg in channel.history(limit=10, oldest_first=True)]
                if len(dm_history) == 0:
                    await channel.send('Loading...')
                for msg_index in range(0, len(dm_history)):
                    if msg_index < len(dm_history)-1:
                        await dm_history[msg_index].delete()
                    else:
                        await dm_history[msg_index].edit(content="Your colonies are currently kept secret", embed=None)
        history = [message async for message in self.log_channel.history(before=leaked_colonies["last_update"] - datetime.timedelta(seconds=20), after=previous_last_update)] #before=date - datetime.timedelta(seconds=20),
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
                            await dm_history[msg_index].delete()     
        self.bot.db.update_leaked_colonies(leaked_colonies_updated)
        
    @tasks.loop(minutes=1)
    async def check_if_war(self):
        print("Infos: check_if_war started")
        now: datetime.datetime = datetime.datetime.now()
        date_time_str: str = now.strftime("%H:%M:%S")
        leaked_colonies = self.bot.db.get_leaked_colonies()
        actual_war: War_Model = self.bot.db.get_one_war("status", "InProgress")
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