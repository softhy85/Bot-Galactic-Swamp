# This example requires the 'message_content' intent.
import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from src.Historic import Historic
from src.War import War
from src.Alliance import Alliance
from src.Player import Player
from src.Colony import Colony
from src.RefreshInfos import RefreshInfos
from src.Role import Role
from src.DataBase import DataBase
from src.Dashboard import Dashboard
from src.GalaxyLifeAPI import GalaxyLifeAPI

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
db = DataBase()
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))

@bot.event
async def on_ready():
    bot.refreshinfo = RefreshInfos(bot, bot.get_guild(int(os.getenv("SERVER_ID"))))
    bot.dashboard = Dashboard(bot, bot.get_guild(int(os.getenv("SERVER_ID"))))
    bot.war = War(bot)
    bot.galaxylifeapi = GalaxyLifeAPI()
    bot.db = db
    bot.spec_role = Role()
    await bot.load_extension("src.Historic")
    await bot.load_extension("src.War")
    await bot.load_extension("src.Alliance")
    await bot.load_extension("src.Player")
    await bot.load_extension("src.Colony")
    await bot.load_extension("src.RefreshInfos")
    print("The bot is online")
    bot.command_channel_id: int = int(os.getenv("COMMAND_CHANNEL"))
    bot.command_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = bot.get_channel(bot.command_channel_id)
    await bot.command_channel.send("@personne - Le bot est connecté. <:O_:1043627742723317770>")


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


bot.run(token)
