# This example requires the 'message_content' intent.
import asyncio
import json
import os
import random
import sys
import time
from datetime import timedelta
from typing import List
from inspect import getcallargs
import discord
import requests
from discord import Guild, app_commands, ui
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, Select, View
from discord.utils import utcnow
from dotenv import load_dotenv
import re

load_dotenv()
token: str = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot: commands.Bot = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"), allowed_mentions = discord.AllowedMentions(everyone = True))
client = discord.Client(intents=intents)
@bot.event
async def on_ready():
    print("The bot is online")
    bot.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
    bot.command_channel = bot.get_channel(bot.command_channel_id)
    bot.war_channel_id = int(os.getenv("WAR_CHANNEL"))
    bot.war_channel = bot.get_channel(bot.war_channel_id)
    bot.ocr_channel_id = int(os.getenv("OCR_CHANNEL"))
    bot.ocr_channel = bot.get_channel(bot.ocr_channel_id)
    bot.general_channel_id = int(os.getenv("GENERAL_CHANNEL"))
    bot.general_channel = bot.get_channel(bot.general_channel_id)
    bot.raw_channel_id = int(os.getenv("RAW_CHANNEL"))
    bot.raw_channel = bot.get_channel(bot.raw_channel_id)
    bot.machine_id = os.getenv("MACHINE_ID")
    bot.easter: int = 0
    bot.path = 'Bot-OCR\\Processed'
    bot.path_unprocessed = "Bot-OCR\\Unprocessed"
    bot.path_processed = "Bot-OCR\\Processed"
    await bot.command_channel.send(f"> `[{bot.machine_id}]` -📝 The OCR bot is **online**. ✨")
    # await generate_message()
    message, user = await client.wait_for('message')
    reaction, user = await client.wait_for('reaction_add')

    
    

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
#     if message.channel == bot.raw_channel:
#         it: int = 0
#         async for message in bot.raw_channel.history(oldest_first=True, limit=10): #, limit=1
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
        for it in range(0, len(data['Proposal'][data['Players'][it_player]])):
            if it < 20:
                options.append(discord.SelectOption(label=data['Proposal'][data['Players'][it_player]][it], emoji="💫", default=False))
        options.append(discord.SelectOption(label="No good answer", emoji="❌", default=False))  
        select = Select(min_values=1, max_values=1, options = options, placeholder=f"{it_player + 1} - {data['Players'][it_player]}", custom_id=data['Players'][it_player])  
        view.add_item(select)
        async def my_callback(interaction):
            print('selected value:', select.values[0])
            for it_player in range(0, len(data['Players'])):
                print(data['Players'][it_player], select.custom_id)
                if data['Players'][it_player] == select.custom_id:
                    print(select.values)
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
                        print("Menu_number")
                        print(data['Players'][it_player])
                        for it in range(0, len(data['Proposal'])):
                            print('1')
                            if  data['Players'][it_player] in data["Proposal"]:
                                print('found and decide to remove')
                                view.remove_item(view.children[it])
                                await button_write_name(view, data, it_player, content)  
                                data["No_Result"].append(data['Players'][it_player])
                                data["Menu_number"] -= 1
                                await interaction.response.edit_message(view=view)
                                break
        select.callback = my_callback
        
        
async def add_button(data, view, content):
    print('enters 1')
    for it_player in range(0, len(data['Players'])):
        
        if data['Players'][it_player] in data["No_Result"]:
            print('yes')
            await button_write_name(view, data, it_player, content)
    if view is not None:
        return view
    else:
        return 

def get_data():
    for file in os.listdir(bot.path):
        if file.endswith(".json"):
            print(file)
            file_chosen = file
            break
    with open(f'{bot.path}\{file_chosen}') as fp:
        data = json.load(fp)  
    return data

def parse_location(data):
    print(data["Location"])
    # location = data["Location"].replace(" ", "")
    
    # location_list = list(location.split(","))
    # data["Location"] = location_list
    location_list = data["Location"]
    print(data)
    return data

def get_screen(data):
    filename = f"{data['Location'][0]}_{data['Location'][1]}.png"
    file = discord.File(f"{bot.path}\{filename}", filename=filename)
    return file

async def store_colonies(data):
    content = ""
    for player in data['Players']:
        content += f"**{player}**: {data['Location'][0]} : {data['Location'][1]}\n"
    if os.path.isfile(f"{bot.path}\{data['Location'][0]}_{data['Location'][1]}.png"):
        print('removing')
        async for message in bot.ocr_channel.history(limit=10):
            coord_x = []
            coord_y = []
            coord_x.append([m.start() for m in re.finditer(f"{data['Location'][0]}", message.content)])
            coord_y.append([m.start() for m in re.finditer(f"{data['Location'][1]}", message.content)])
            if coord_x != [[]] and coord_y != [[]]:
                time.sleep(1)
                await message.delete()
                print('found')
            # if message.content[]
        os.remove(f"{bot.path}\{data['Location'][0]}_{data['Location'][1]}.png")
        for file in os.listdir(bot.path):
            if file.endswith(".json"):
                print(file)
                os.remove(f"{bot.path}\{file}")
                break
    await generate_message()
    

async def generate_message():
    view = View(timeout=None)
    data = get_data()
    content = f"> 🪐 **{data['Name']}**  🔍 ``{data['Location']}``  `"
    print(content)
    true_number: int = 0
    for it in range(0, len(data['Players'])):
        if data['Ready_to_store'][it] == True:
            content = content + "✅"
            true_number += 1
        else:
            content = content + "🔳"
    content = content + "`"
    if true_number == len(data["Players"]):
        await store_colonies(data)
    print('before')
    data = parse_location(data)
    print('after')
    file = get_screen(data)
    print('got the screen')
    view = await add_menu(data, view, content)
    view = await add_button(data, view, content)
    print('hohoho')
    await bot.ocr_channel.send(content=content, file=file, view=view) #, attachment="Bot-OCR\screenshot.png"

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