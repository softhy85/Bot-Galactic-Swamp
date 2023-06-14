# This example requires the 'message_content' intent.
import asyncio
import os
import random
import sys
import time
from datetime import timedelta
from typing import List
import requests

import discord
from discord import Guild, app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.utils import utcnow
from dotenv import load_dotenv
from Models.Next_War_Model import Next_War_Model
from Utils.Alliance import Alliance
from Utils.Autocomplete import Autocomplete
from Utils.Dashboard import Dashboard
from Utils.DataBase import DataBase
from Utils.GalaxyCanvas import GalaxyCanvas
from Utils.GalaxyLifeAPI import GalaxyLifeAPI
from Utils.Role import Role

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
app_name: str = os.getenv("APP_NAME")
intents = discord.Intents.default()
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
    bot.galaxyCanvas = GalaxyCanvas(bot)
    bot.autocomplete = Autocomplete(bot)
    bot.galaxyLifeAPI = GalaxyLifeAPI()
    bot.alliance = Alliance(bot)
    bot.spec_role = Role()
    bot.dashboard = Dashboard(bot)
    flush_logs_out.start()
    bot.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
    bot.command_channel = bot.get_channel(bot.command_channel_id)
    bot.war_channel_id = int(os.getenv("WAR_CHANNEL"))
    bot.war_channel = bot.get_channel(bot.war_channel_id)
    bot.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
    bot.general_channel = bot.get_channel(bot.general_channel_id)
    bot.machine_id = os.getenv("MACHINE_ID")
    bot.raw_backup_channel_id = int(os.getenv("RAW_BACKUP_CHANNEL"))
    bot.raw_backup_channel = bot.get_channel(bot.raw_backup_channel_id)
    bot.processed_backup_channel_id = int(os.getenv("PROCESSED_BACKUP_CHANNEL"))
    bot.processed_backup_channel = bot.get_channel(bot.processed_backup_channel_id)
    bot.processed_channel_id = int(os.getenv("PROCESSED_CHANNEL"))
    bot.processed_channel = bot.get_channel(bot.processed_channel_id)
    bot.raw_channel_id = int(os.getenv("RAW_CHANNEL"))
    bot.raw_channel = bot.get_channel(bot.raw_channel_id)
    bot.easter: int = 0
    bot.path = os.getenv("PROGRAM_PATH")
    await bot.command_channel.send(f"> `[{bot.machine_id}]` - The bot is **online**. ✨")
    cogs: List[str] = list(["Cogs.Cog_Historic", "Cogs.Cog_Refresh", "Cogs.Cog_War", "Cogs.Cog_Alliance", "Cogs.Cog_Player", "Cogs.Cog_Colony", "Cogs.Cog_Misc", "Cogs.Cog_Scout"])
    for cog in cogs:
        await bot.load_extension(cog)
    reaction, user = await client.wait_for('reaction_add')
    reaction, user = await client.wait_for('reaction_remove')
    
@tasks.loop(seconds=1)
async def flush_logs_out():
    sys.stdout.flush()

@flush_logs_out.before_loop
async def before_flush_logs_out():
    await bot.wait_until_ready()

@bot.command()
async def sync(ctx: Context) -> None:
    if bot.spec_role.admin_role(ctx.guild, ctx.author):
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(fmt)} commands.')
    else:
        await ctx.send("You don't have the permission to use this command.")
    
@bot.command(pass_context=True)
async def clear(ctx, number):
    number = int(number)
    await ctx.channel.purge(limit=number)

@bot.event
async def on_raw_reaction_add(reaction):
    update: bool = False
    if reaction.channel_id == bot.war_channel_id:
        next_war: Next_War_Model = bot.db.get_nextwar()
        if reaction.emoji.name == "👍🏻":
            if reaction.member.name != app_name:
                if reaction.member.nick == None:
                    name = reaction.member.name
                else:
                    name = reaction.member.nick
                await bot.general_channel.send(f"> **{name}** has voted to start a war. Come to https://discord.com/channels/1043524633602826294/1043548046602014831 to vote too!")
                next_war['positive_votes'] = next_war['positive_votes'] + 1
                update = True
        if reaction.emoji.name == "👎🏻":
            next_war['negative_votes'] = next_war['negative_votes'] + 1
            update = True
        if update == True:
            bot.db.update_nextwar(next_war) 
            cog_war = bot.get_cog('Cog_War')
            if cog_war is not None:
                await cog_war.update_peace_embed()

@bot.event
async def on_raw_reaction_remove(reaction):
    update: bool = False
    if reaction.channel_id == bot.war_channel_id:
        next_war: Next_War_Model = bot.db.get_nextwar()
        if reaction.emoji.name == "👍🏻":
            next_war['positive_votes'] = next_war['positive_votes'] - 1
            update = True
        if reaction.emoji.name == "👎🏻":
            next_war['negative_votes'] = next_war['negative_votes'] - 1
            update = True
        if update == True:
            bot.db.update_nextwar(next_war) 
            cog_war = bot.get_cog('Cog_War')
            if cog_war is not None:
                await cog_war.update_peace_embed()

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
        easter_number = random.randint(1, 2)
        if bot.easter == 0:
            await ctx.send("> There is no command named like this. 👀 \n")
        if bot.easter >= 1:
            if bot.easter == 1:
                await ctx.send("``Don't you dare talking in my langage ! 🧐``")
            if bot.easter == 2:
                await ctx.send("``Wanna fight ????? 🤬``")
            if bot.easter == 3:
                await ctx.send("``I guess you're stupid or something... 🙃``")
            if bot.easter == 4:
                await ctx.send("``Stop. ⚔️``")
            if bot.easter == 5:
                await ctx.send("``So you think you are safe from me ??? 😠``")
            if bot.easter == 6:
                await ctx.send("``...😈``")
            if bot.easter == 7:
                await ctx.send(f"``{ctx.author.display_name}, i'll find you and and...``")
            if bot.easter == 8:
                await ctx.send(f"``OKAY. GOT IT.``")
                time.sleep(4)
                await ctx.send(f"> @everyone we are at war against **CIEPLE DRANIE**")
                time.sleep(2)
                await ctx.send(f"(Top 1)")
                time.sleep(2)
                await ctx.send(f"(GG no win)")
                time.sleep(2)
                await ctx.send(f"(Good luck... NO)")
                time.sleep(2)
                await ctx.send(f"(I hate you)")
                time.sleep(2)
                await ctx.send(f"(I will leave this server)")
            if bot.easter >= 9:
                await ctx.send(':middle_finger::skin-tone-1:')
                if bot.easter == 10:
                    await ctx.send(f"``Here's a picture of {ctx.author.display_name}'s house. Coords: 51.502977, 5.391268  https://www.google.fr/maps/place/51%C2%B030'10.7%22N+5%C2%B023'28.6%22E/@51.5028668,5.3900556,17z/data=!4m4!3m3!8m2!3d51.502977!4d5.391268`` https://media.istockphoto.com/id/1347190073/photo/dutch-suburban-area-with-modern-family-houses-newly-build-modern-family-homes-in-the.jpg?s=612x612&w=0&k=20&c=KpHXCY4HI_hSCccYQnyT1sgjdqSAQ0lsvHKlsTFepXo=")
            bot.easter += 1
        if easter_number == 1 and bot.easter == 0:
            time.sleep(5)
            await ctx.send("``Also don't tell me to shut up, i'm a bot and i have rights,`` \n``and also feelings, and i wont permit you to talk to me this way. ☠️``")
            bot.easter = 1
        

@bot.command(pass_context=True)
async def woops(ctx: Context, content: int):
    await  ctx.send(f"> :flag_fr: Damn, you fucked up once again? [FRENCH BOT] will fix that for you 🥖")
    hist_list = [hist_list async for hist_list in bot.raw_backup_channel.history(limit=content)]
    for file in os.listdir(f"{bot.path}/Test"):
        if file.endswith(".png"):
            path = os.path.join(f"{bot.path}/Test", file)
            try:
                os.remove(f"D:\💻 DOCUMENTS\🛠 Programmation\Bot-Galactic-Swamp\Bot-War\Test\{file}")
            except OSError as e: # name the Exception `e`
                print ("Failed with:", e.strerror )# look what it says
                print ("Error code:", e.code )
    it: int = 0
    it_max: int = len(hist_list)     
    for message in hist_list:
        print('remaing:', it_max - it, "/", it_max)
        it += 1
        if message.content == "API request failed":
            for file in message.attachments:
                if file.filename.endswith(".png") == True:
                    file_path = file
                    files = []
                    myfile = requests.get(file_path)
                    with open(f"{bot.path}/Test/{file.filename}", "wb") as outfile:
                        outfile.write(myfile.content)
                        outfile.close()
            for file in os.listdir(f"{bot.path}/Test"):
                if file.endswith(".png"):
                    file_saved = discord.File(f'{bot.path}/Test/{file}', filename=f"{file}")
                    files.append(file_saved)
            await message.delete()
            await bot.raw_channel.send(content="", files=files)
    await ctx.send("I've fixed all for you. But dont make that mistake again 😎")
    

@bot.command(pass_context=True)
async def transfer(ctx: Context, content: int):
    await  ctx.send(f"> :flag_fr: Damn, you fucked up once again? [FRENCH BOT] will fix that for you 🥖")
    hist_list = [hist_list async for hist_list in bot.processed_backup_channel.history(limit=content)]
    for file in os.listdir(f"{bot.path}/Test"):
        if file.endswith(".png"):
            path = os.path.join(f"{bot.path}/Test", file)
            try:
                os.remove(f"D:\💻 DOCUMENTS\🛠 Programmation\Bot-Galactic-Swamp\Bot-War\Test\{file}")
            except OSError as e: # name the Exception `e`
                print ("Failed with:", e.strerror )# look what it says
                print ("Error code:", e.code )
    it: int = 0
    it_max: int = len(hist_list)     
    for message in hist_list:
        print('remaing:', it_max - it, "/", it_max)
        it += 1

        for file in message.attachments:
            if file.filename.endswith(".png") == True:
                file_path = file
                files = []
                myfile = requests.get(file_path)
                with open(f"{bot.path}/Test/{file.filename}", "wb") as outfile:
                    outfile.write(myfile.content)
                    outfile.close()
        for file in os.listdir(f"{bot.path}/Test"):
            if file.endswith(".png"):
                file_saved = discord.File(f'{bot.path}/Test/{file}', filename=f"{file}")
                files.append(file_saved)
        #await message.delete()
            
        await bot.processed_channel.send(content=message.content, files=files)
    await ctx.send("I've fixed all for you. But dont make that mistake again 😎")

    
@bot.command(pass_context=True)
async def fuck(ctx: Context, message_id: int):
    await  ctx.send(f"> :flag_fr: Damn, you fucked up once again? [FRENCH BOT] will fix that for you 🥖")
    print('-1')
    message = await bot.raw_backup_channel.fetch_message(message_id)
    print('0')
    for file in os.listdir(f"{bot.path}/Test"):
        if file.endswith(".png"):
            path = os.path.join(f"{bot.path}/Test", file)
            try:
                os.remove(f"D:\💻 DOCUMENTS\🛠 Programmation\Bot-Galactic-Swamp\Bot-War\Test\{file}")
            except OSError as e: # name the Exception `e`
                print ("Failed with:", e.strerror )# look what it says
                print ("Error code:", e.code )   
    print('2')
    for file in message.attachments:
        if file.filename.endswith(".png") == True:
            file_path = file
            files = []
            myfile = requests.get(file_path)
            with open(f"{bot.path}/Test/{file.filename}", "wb") as outfile:
                outfile.write(myfile.content)
                outfile.close()
    print('3')
    for file in os.listdir(f"{bot.path}/Test"):
        if file.endswith(".png"):
            file_saved = discord.File(f'{bot.path}/Test/{file}', filename=f"{file}")
            files.append(file_saved)
    print('4')
    await message.delete()
    await bot.raw_channel.send(content=message.content, files=files)
    await ctx.send("I've fixed all for you. But dont make that mistake again 😎")


@bot.command()
async def disconnect(ctx: Context):
    if bot.spec_role.admin_role(ctx.guild, ctx.author):
        await bot.command_channel.send(f"> `[{bot.machine_id}]` - The war bot is **shutting down**. 💢")
        print("Closing the bot.")
        bot.db.close()
        await bot.close()
        exit(0)

async def main():
    async with bot:
        # await load_extensions(bot)
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())