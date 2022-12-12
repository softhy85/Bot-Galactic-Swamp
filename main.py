# This example requires the 'message_content' intent.
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.Historic import Historic

if __name__ == '__main__':
    load_dotenv()
    token: str = os.getenv("BOT_TOKEN")
    intents = discord.Intents.default()
    intents.members = True
    bot: commands.Bot = commands.Bot(command_prefix=">", intents=intents)

    @bot.event
    async def on_ready():
        print("Bot is online !")
        await bot.add_cog(Historic(bot))

    bot.run(token)
