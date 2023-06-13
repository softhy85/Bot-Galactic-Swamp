# This example requires the 'message_content' intent.
import asyncio
import datetime
import json
import os
import random
import re
import sys
import time
from inspect import getcallargs
from typing import List

import discord
import requests
from discord import Guild, app_commands, ui
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, Select, View
from discord.utils import utcnow
from dotenv import load_dotenv
from Utils.DataBase import DataBase

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
app_name: str = os.getenv("APP_NAME")
intents = discord.Intents().all()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True), help_command=None)
bot.remove_command("help")
client = discord.Client(intents=intents)
@bot.event
async def on_ready():
    print("The bot is online")
    bot.db = db
    bot.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
    bot.command_channel = bot.get_channel(bot.command_channel_id)
    bot.war_channel_id = int(os.getenv("WAR_CHANNEL"))
    bot.war_channel = bot.get_channel(bot.war_channel_id)
    bot.ocr_channel_id = int(os.getenv("OCR_CHANNEL"))
    bot.ocr_channel = bot.get_channel(bot.ocr_channel_id)
    bot.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
    bot.general_channel = bot.get_channel(bot.general_channel_id)
    bot.log_channel_id = int(os.getenv("LOG_CHANNEL"))
    bot.log_channel = bot.get_channel(bot.log_channel_id)
    bot.machine_id = os.getenv("MACHINE_ID")
    await bot.command_channel.send(f"> `[{bot.machine_id}]` -🪐 The Leak bot is **online**. ✨")
    cogs: List[str] = list(["Cogs.Cog_Tasks"])
    for cog in cogs:
        await bot.load_extension(cog)
    # await generate_message()
    message, user = await client.wait_for('message')
    reaction, user = await client.wait_for('reaction_add')
    reaction, user = await client.wait_for('reaction_remove')
    

@bot.event
async def on_raw_reaction_add(reaction: discord.reaction):
    user_dm=await bot.fetch_user(int(reaction.member.id))
    user_channel = user_dm.dm_channel
    if reaction.channel_id == bot.war_channel_id:
        # member: discord.Member = reaction.member
        # member.id
        if reaction.emoji.name == "🪐":
            if reaction.member.name != app_name:
                leaked_colonies = bot.db.get_leaked_colonies()
                print(reaction.member.id)
                if not str(reaction.member.id) in leaked_colonies['registered_users']:
                    print('adding the user')
                    leaked_colonies['registered_users'].append(str(reaction.member.id))
                    bot.db.update_leaked_colonies(leaked_colonies)
                    user_dm=await bot.fetch_user(int(reaction.member.id))
                    if user_dm.dm_channel is not None:
                        channel = user_dm.dm_channel
                    else:
                        channel = await user_dm.create_dm()
                    message = await channel.send("```You just registered to the colo leak tool 🪐. You will be able to mark which of your colonies you leaked to any player. This way you will attack wisely and not share your coordinates. React under this message to disable it```")
                    await message.add_reaction("❌")
                else: 
                    print('user is already registered')
    elif reaction.member.name != app_name:
        if user_channel.id == reaction.channel_id:
            if reaction.emoji.name == "❌":
                print('unsus')

# @bot.event
# async def on_raw_reaction_remove(reaction: discord.reaction):
#     update: bool = False
#     print('removed reaction')
#     if reaction.channel_id == bot.war_channel_id:
#         # member: discord.Member = reaction.member
#         # member.id
#         if reaction.emoji.name == "🪐":
#             print(reaction.member)
#             print('removed colo emoji')
#             if reaction.member.name != app_name:
#                 print('damn')
#                 leaked_colonies = bot.db.get_leaked_colonies()
#                 print(reaction.member.id)
#                 if not str(reaction.member.id) in leaked_colonies['registered_users']:
#                     print('removing the user')
#                     leaked_colonies['registered_users'].remove(str(reaction.member.id))
#                     print(leaked_colonies['registered_users'])
#                     bot.db.update_leaked_colonies(leaked_colonies)
#                 else: 
#                     print('user is already part of registration')
                    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        if bot.easter == 0:
            await ctx.send("> There is no command named like this. 👀 \n")     

@bot.command()
async def disconnect(ctx):
    await bot.command_channel.send(f"> `[{bot.machine_id}]` - 🪐 The Leak bot is **shutting down**. 💢")
    print("Closing the bot.")
    bot.db.close()
    await bot.close()
    exit(0)

async def main():
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())