# This example requires the 'message_content' intent.
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.Historic import Historic
from src.War import War
from src.Role import Role
from src.DataBase import DataBase

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))

@bot.event
async def on_ready():
    print("The bot is online")
    await bot.load_extension("src.Historic")
    await bot.load_extension("src.War")


@commands.command()
async def disconnect(member: discord.Member):
    number_role = len(member.roles)
    for x in range(0, number_role):
        role: discord.Role = member.roles[x]
        if role.name == "Admin":
            print("Closing the bot.")
            db.close()
            exit(0)

bot.db = db
bot.spec_role = Role()

bot.run(token)
