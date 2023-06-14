# This example requires the 'message_content' intent.
import asyncio
import json
import os
import random
import re
import sys
import time
from datetime import timedelta
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
from Models.Found_Colony_Model import Found_Colony_Model
from Utils.DataBase import DataBase
from Utils.GalaxyLifeAPI import GalaxyLifeAPI

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True), help_command=None)
bot.remove_command("help")
client = discord.Client(intents=intents)
db = DataBase()


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
    bot.processed_channel_id = int(os.getenv("PROCESSED_CHANNEL"))
    bot.processed_channel = bot.get_channel(bot.processed_channel_id)
    bot.machine_id = os.getenv("MACHINE_ID")
    bot.easter: int = 0
    bot.program_path = os.getenv("PROGRAM_PATH")
    bot.path = f'{bot.program_path}/Processed'
    bot.path_unprocessed = f'{bot.program_path}/Unprocessed'
    bot.path_processed = "Bot-OCR/Processed"
    bot.galaxyLifeAPI = GalaxyLifeAPI()
    print('before loagind cogs')
    cogs: List[str] = list(["Cogs.Cog_API_Process"])
    for cog in cogs:
        await bot.load_extension(cog)
    print('after loading cogs')
    await bot.command_channel.send(f"> `[{bot.machine_id}]` -📝 The OCR (API Process) bot is **online**. ✨")
    
    message, user = await client.wait_for('message')
    reaction, user = await client.wait_for('reaction_add')


class MyHelp(commands.HelpCommand):
   # !help
    async def help(self):
        await self.context.send("This is help")        

@bot.command()
async def disconnect(ctx):
    await bot.command_channel.send(f"> `[{bot.machine_id}]` - 📝 The OCR (API Process) bot is **shutting down**. 💢")
    print("Closing the bot.")
    bot.db.close()
    await bot.close()
    exit(0)

async def main():
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())