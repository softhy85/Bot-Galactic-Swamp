# This example requires the 'message_content' intent.
import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from Cogs.Cog_Historic import Cog_Historic
from Cogs.Cog_War import Cog_War
from Cogs.Cog_Alliance import Cog_Alliance
from Cogs.Cog_Player import Cog_Player
from Cogs.Cog_Colony import Cog_Colony
from Utils.Alliance import Alliance
from Utils.RefreshInfos import RefreshInfos
from Utils.Role import Role
from Utils.DataBase import DataBase
from Utils.Dashboard import Dashboard
from Utils.GalaxyLifeAPI import GalaxyLifeAPI

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))

@bot.event
async def on_ready():
    bot.alliance = Alliance(bot)
    bot.refreshInfos = RefreshInfos(bot, bot.get_guild(int(os.getenv("SERVER_ID"))))
    bot.dashboard = Dashboard(bot, bot.get_guild(int(os.getenv("SERVER_ID"))))
    bot.galaxyLifeAPI = GalaxyLifeAPI()
    bot.db = db
    bot.spec_role = Role()
    bot.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
    bot.command_channel = bot.get_channel(bot.command_channel_id)
    await bot.command_channel.send("@personne - Le bot est connecté. <:O_:1043627742723317770>")
    print("The bot is online")


@bot.command()
async def sync(ctx: Context) -> None:
    if bot.spec_role.admin_role(ctx.guild, ctx.author):
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(fmt)} commands.')
    else:
        await ctx.send("You don't have the permission to use this command.")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        await interaction.response.send_message(f'Command {interaction.command.name} is on cooldown, you can use it in {round(error.retry_after, 2)} seconds.', ephemeral=True)
    elif isinstance(error, app_commands.errors.CommandNotFound):
        await interaction.response.send_message(f"There is no command named {interaction.command.name}.", ephemeral=True)
    elif isinstance(error, app_commands.errors.MissingAnyRole):
        await interaction.response.send_message(f"You do not have the role tu use {interaction.command.name} command.", ephemeral=True)
    elif isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(f"You do not have the role tu use {interaction.command.name} command.", ephemeral=True)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("There is no command named like this.")

@bot.command()
async def disconnect(ctx: Context):
    if bot.spec_role.admin_role(ctx.guild, ctx.author):
        await bot.command_channel.send("@everyone - Le bot est déconnecté !!!")
        print("Closing the bot.")
        bot.db.close()
        await bot.close()
        exit(0)


await bot.load_extension("Utils.Cog_Historic")
await bot.load_extension("Utils.Cog_War")
await bot.load_extension("Utils.Cog_Alliance")
await bot.load_extension("Utils.Cog_Player")
await bot.load_extension("Utils.Cog_Colony")
bot.run(token)
