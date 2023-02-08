# This example requires the 'message_content' intent.
import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from src.Historic import Historic
from src.War import War
from src.Alliance import Alliance
from src.Player import Player
from src.Colony import Colony
from src.Role import Role
from src.DataBase import DataBase
from src.Dashboard import Dashboard

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))

@bot.event
async def on_ready():
    bot.dashboard = Dashboard(bot, bot.get_guild(int(os.getenv("SERVER_ID"))))
    bot.db = db
    bot.spec_role = Role()
    print("The bot is online")
    await bot.load_extension("src.Historic")
    await bot.load_extension("src.War")
    await bot.load_extension("src.Alliance")
    await bot.load_extension("src.Player")
    await bot.load_extension("src.Colony")

@bot.command()
async def sync(ctx: Context) -> None:
    if bot.spec_role.admin_role(ctx.guild, ctx.author):
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(fmt)} commands.')
    else:
        await ctx.send("You don't have the permission to use this command.")


@bot.command()
async def disconnect(ctx: Context):
    if bot.spec_role.admin_role(ctx.guild, ctx.author):
        print("Closing the bot.")
        bot.db.close()
        await bot.close()
        exit(0)


bot.run(token)
