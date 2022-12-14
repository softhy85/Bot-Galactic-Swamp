# This example requires the 'message_content' intent.
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.Historic import Historic
from src.War import War

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"))


@bot.event
async def on_ready():
    print("The bot is online")
    await bot.load_extension("src.Historic")
    await bot.load_extension("src.War")
#    await bot.add_cog(historic(bot))
#    await bot.add_cog(War(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])


bot.run(token)
