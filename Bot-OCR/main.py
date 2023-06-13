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
from Processing import Processing
from Utils.DataBase import DataBase
from Utils.GalaxyLifeAPI import GalaxyLifeAPI

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))
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
    bot.processing  = Processing(bot)
    bot.galaxyLifeAPI = GalaxyLifeAPI()
    await bot.command_channel.send(f"> `[{bot.machine_id}]` -📝 The OCR bot is **online**. ✨")
    await start()
    
    message, user = await client.wait_for('message')
    reaction, user = await client.wait_for('reaction_add')


class MyHelp(commands.HelpCommand):
   # !help
    async def help(self):
        await self.context.send("This is help")
        
async def start():
    data = None
    stock = await get_processed_channel_length()
    screen_number = len(list(bot.db.get_all_found_colonies()))
    print('stock', stock)
    embed = discord.Embed(title='✅ Screened Colonies', description=f'📸 Screens remaining: `{stock}`\n🪐 Colonies screened so far: `{screen_number}`')
    
    hist_list = [hist_list async for hist_list in bot.ocr_channel.history(limit=10, oldest_first=False)]
    if_embed = False
    if len(hist_list) >= 2:
        print('enters')
        for message in hist_list:
            print(message.embeds)
            if message.embeds != []:
                if message.embeds[0].title[0] == "✅":
                    print('there is the embed')
                    await message.edit(embed=embed)
                    if_embed = True
        if if_embed == False:
            await bot.ocr_channel.send(embed=embed)
    print('then')
    processed_messages = [processed_messages async for processed_messages in bot.processed_channel.history(limit=10)]
    while len(processed_messages) == 0:
        processed_messages = [processed_messages async for processed_messages in bot.processed_channel.history(limit=10)]
    print('found messages in processed')
    

    hist_list = [hist_list async for hist_list in bot.ocr_channel.history(limit=10)]
    print('history made')
    while len(hist_list) < 4 or hist_list == []:
        print('currently not enough messages (', len(hist_list), ')')
        while len(processed_messages) == 0:
            processed_messages = [processed_messages async for processed_messages in bot.processed_channel.history(limit=10)]
        print('escaping the while loop')
        data = await bot.processing.process()
        await generate_message(data)
    
        
async def get_processed_channel_length():
    channel = bot.processed_channel
    count = 0
    async for _ in channel.history(limit=None):
        count += 1
    return count
    
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

# @bot.event
# async def on_message(message):
#     if message.channel == bot.processed_channel:
#         it: int = 0
#         async for message in bot.processed_channel.history(oldest_first=True, limit=10): #, limit=1
#             # for attachment in message.attachments:
#             attachment = message.attachments[0]
#             if attachment.filename.endswith(".png") == True:
#                 print(message.attachments[0])
#                 file_path = message.attachments[it]
#                 myfile = requests.get(file_path)
#                 with open(f"{bot.path_unprocessed}/screen_{it+1}.png", "wb") as outfile:
#                     outfile.write(myfile.content)
#                 it += 1       
                # if it >= 2:
                #     break          

                       
async def add_menu(data, view, content):
    for it_player in range(0, len(data['Players'])):
        if  data['Players'][it_player] in data["Proposal"]:
            await menu(data, view, it_player, content)
            data["Menu_number"] += 1
    return (view)

async def menu(data, view, it_player, content):
        options: List[discord.SelectOption] = []
        options.append(discord.SelectOption(label="No good answer", emoji="❌", default=False))  
        for it in range(0, len(data['Proposal'][data['Players'][it_player]])):
            if it < 20:
                
                options.append(discord.SelectOption(label=data['Proposal'][data['Players'][it_player]][it], emoji="💫", default=False))
        select = Select(min_values=1, max_values=1, options = options, placeholder=f"{it_player + 1} - {data['Players'][it_player]}", custom_id=data['Players'][it_player])  
        view.add_item(select)
        
        async def my_callback(interaction):
            print('selected value:', select.values[0])
            for it_player in range(0, len(data['Players'])):
                if data['Players'][it_player] == select.custom_id:
                    if select.values[0] != "No good answer":
                        data['Players'][it_player] = select.values[0]
                        data['Ready_to_store'][it_player] = True
                        string = str(content)
                        string = string[0:-len(data['Players'])-1]
                        true_number = 0
                        for it in range(0, len(data['Players'])):
                            if data['Ready_to_store'][it] == True:
                                string = string + "✅"
                                true_number += 1
                            else:
                                string = string + "🔳"
                        string = string + "`"
                        await interaction.response.edit_message(content=string)  
                        if true_number == len(data['Players']):
                            await store_colonies(data)
                    else:
                        for it in range(0, len(data['Proposal'])):
                            if  data['Players'][it_player] in data["Proposal"]:
                                view.remove_item(view.children[it])
                                await button_write_name(view, data, it_player, content)  
                                data["No_Result"].append(data['Players'][it_player])
                                data["Menu_number"] -= 1
                                await interaction.response.edit_message(view=view)
                                break
        select.callback = my_callback
        
        
async def add_button(data, view, content):
    for it_player in range(0, len(data['Players'])):
        
        if data['Players'][it_player] in data["No_Result"]:
            await button_write_name(view, data, it_player, content)
    if view is not None:
        return view
    else:
        return 


def parse_location(data):
    # location = data["Location"].replace(" ", "")
    # location_list = list(location.split(","))
    # data["Location"] = location_list
    location_list = data["Location"]
    return data

def get_screen(data):
    filename = f"{data['Location'][0]}_{data['Location'][1]}.png"
    file = discord.File(f"{bot.path}/{filename}", filename=filename)
    return file


def db_handle(data):
    for player in data['Players']:
        player_infos = bot.galaxyLifeAPI.get_player_infos_from_name(player)
        player_id = player_infos['player_id_gl']        
        print(f"attempting to store colony:  {player} ({player_id}): {data['Title']}({data['Location']})")
        colony: Found_Colony_Model = {'gl_id': player_id, 'colo_sys_name':data['Title'], 'X': int(data['Location'][0]), 'Y':int(data['Location'][1])}
        bot.db.push_found_colony(colony)
        
async def store_colonies(data):
    content = ""
    for player in data['Players']:
        content += f"**{player}**: {data['Location'][0]} : {data['Location'][1]}\n"
    if os.path.isfile(f"{bot.path}\{data['Location'][0]}_{data['Location'][1]}.png"):
        async for message in bot.ocr_channel.history(limit=10):
            coord_x = []
            coord_y = []
            coord_x.append([m.start() for m in re.finditer(f"{data['Location'][0]}", message.content)])
            coord_y.append([m.start() for m in re.finditer(f"{data['Location'][1]}", message.content)])
            if coord_x != [[]] and coord_y != [[]]:
                time.sleep(1)
                print('should delete')
                await message.delete()
            # if message.content[]
        os.remove(f"{bot.path}\{data['Location'][0]}_{data['Location'][1]}.png")
        for file in os.listdir(bot.path):
            if file.endswith(".json"):
                print(file)
                os.remove(f"{bot.path}\{file}")
                break
    db_handle(data)
    await start()
    

async def generate_message(data):
    print('entering generate_message')
    view = View(timeout=None)
    content = f"> 🪐 **{data['Title']}**  🔍 ``{data['Location']}``  `"
    true_number: int = 0
    for it in range(0, len(data['Players'])):
        if data['Ready_to_store'][it] == True:
            content = content + "✅"
            true_number += 1
        else:
            content = content + "🔳"
    content = content + "`"
    if true_number == len(data["Players"]):
        print('✅✅✅ processed result was perfect')
        await store_colonies(data)
    data = parse_location(data)
    file = get_screen(data)
    view = await add_menu(data, view, content)
    view = await add_button(data, view, content)
    print('sending message')
    await bot.ocr_channel.send(content=content, view=view, file=file)

async def button_write_name(view, data, it_player, content): 
    button_write_name = Button(label = f"{data['Players'][it_player]}", style=discord.ButtonStyle.grey)  
    view.add_item(button_write_name)
    async def button_callback_write_name(interaction):
        test_name_1 = data['Players'][it_player]
        class my_modal(ui.Modal, title='Add username'):
            player=ui.TextInput(label='username', style=discord.TextStyle.short, default=f'{test_name_1}', required = True)   
            async def on_submit(self, interaction):
                for player_index in range(0, len(data["No_Result"])):
                    if data["No_Result"][player_index] == test_name_1:
                        child_number = player_index
                        data["No_Result"].append(self.player.value)
                        del data["No_Result"][player_index]
                        break
                test_name = data['Players'][it_player]
                results = requests.get(f'https://api.galaxylifegame.net/Users/name?name={self.player.value}', timeout=1.5)
                if chr(results.content[0]) == '{':  
                    button_write_name = Button(label = f"{self.player.value}", style=discord.ButtonStyle.green)
                    view.remove_item(view.children[child_number+data["Menu_number"]])
                    view.add_item(button_write_name)
                    for index in range(0, len(data["Players"])):
                        if data["Players"][index] == test_name:
                            data['Players'][index] = self.player.value
                            data['Ready_to_store'][index] = True
                else:
                    for index in range(0, len(data["Players"])):
                        if data["Players"][index] == test_name:
                            data['Players'][index] = self.player.value
                            data['Ready_to_store'][index] = False
                            break
                    view.remove_item(view.children[child_number+data["Menu_number"]])
                    button_write_name = Button(label = f"{self.player.value}", style=discord.ButtonStyle.red) 
                    view.add_item(button_write_name)
                button_write_name.callback = button_callback_write_name
                string = str(content)
                string = string[0:-len(data['Players'])-1]
                true_number = 0
                for it in range(0, len(data['Players'])):
                    if data['Ready_to_store'][it] == True:
                        string = string + "✅"
                        true_number += 1
                    else:
                        string = string + "🔳"
                string = string + "`"
                await interaction.response.edit_message(view=view, content=string)
                if true_number == len(data["Players"]):
                    await store_colonies(data)
        await interaction.response.send_modal(my_modal())
    button_write_name.callback = button_callback_write_name  

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        if bot.easter == 0:
            await ctx.send("> There is no command named like this. 👀 \n")     

@bot.command()
async def disconnect(ctx):
    await bot.command_channel.send(f"> `[{bot.machine_id}]` - 📝 The OCR bot is **shutting down**. 💢")
    print("Closing the bot.")
    bot.db.close()
    await bot.close()
    exit(0)

async def main():
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())