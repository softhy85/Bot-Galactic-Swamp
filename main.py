# This example requires the 'message_content' intent.
import asyncio
import os
from typing import List

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from Utils.Alliance import Alliance
from Utils.Role import Role
from Utils.DataBase import DataBase
from Utils.Dashboard import Dashboard
from Utils.GalaxyLifeAPI import GalaxyLifeAPI
from Utils.GalaxyCanvas import GalaxyCanvas
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
    bot.db = db
    bot.galaxyCanvas = GalaxyCanvas(bot)
    bot.galaxyLifeAPI = GalaxyLifeAPI()
    bot.alliance = Alliance(bot)
    bot.spec_role = Role()
    bot.dashboard = Dashboard(bot)
    bot.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
    bot.command_channel = bot.get_channel(bot.command_channel_id)
    await bot.command_channel.send("@personne - Le bot est connecté. <:O_:1043627742723317770>")
    cogs: List[str] = list(["Cogs.Cog_Historic", "Cogs.Cog_Refresh", "Cogs.Cog_War", "Cogs.Cog_Alliance", "Cogs.Cog_Player", "Cogs.Cog_Colony"])
    for cog in cogs:
        await bot.load_extension(cog)


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
        if interaction.command is not None:
            await interaction.response.send_message(f"There is no command named {interaction.command.name}.", ephemeral=True)
        else: 
            await interaction.response.send_message(f"There is no command named {error.name}.", ephemeral=True)
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

# async def load_extensions(bot):
    # for filename in os.listdir('./Cogs'):
    #     if filename.endswith('.py'):
    #         bot.load_extension(f'Cogs.{filename[:-3]}')

async def main():
    async with bot:
        # await load_extensions(bot)
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())