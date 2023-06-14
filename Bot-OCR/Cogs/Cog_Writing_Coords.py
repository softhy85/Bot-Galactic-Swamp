import asyncio
import datetime
import itertools
import json
import os
import re
import time
from collections import Counter
from threading import Thread
from typing import List

import discord
import requests
from discord import ui
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, Select, View
from Models.Found_Colony_Model import Found_Colony_Model


class Cog_Writing_Coords(commands.Cog):
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.username_count = 0
        self.success_count = 0
        self.multiple_answer_count = 0
        self.fail = 0
        self.matching_list = []
        self.program_path_back = os.getenv("PROGRAM_PATH_BACK")
        self.program_path = os.getenv("PROGRAM_PATH")
        self.path = f'{self.program_path}/Processed'
        self.path_ready = f'{self.program_path}/Ready'
        self.path_unprocessed = f'{self.program_path}/Unprocessed'
        self.processed_channel_id = int(os.getenv("PROCESSED_CHANNEL"))
        self.processed_channel = self.bot.get_channel(self.processed_channel_id)
        self.API_processed_channel_id = int(os.getenv("API_PROCESSED_CHANNEL"))
        self.ocr_channel_id = int(os.getenv("OCR_CHANNEL"))
        self.ocr_channel = bot.get_channel(bot.ocr_channel_id)
        self.API_processed_channel = self.bot.get_channel(self.API_processed_channel_id)
        self.worked_first_try = False
        self.task_writing_coords.start()
        self.task_update_embed.start()
    
    @tasks.loop(seconds = 1)
    async def task_writing_coords(self):
        hist_list = [hist_list async for hist_list in self.ocr_channel.history(limit=10)]
        if len(hist_list) < 4 or hist_list == []:
            # print('currently not enough messages (', len(hist_list), ')')
            API_processed_messages = [API_processed_messages async for API_processed_messages in self.API_processed_channel.history(limit=10)]
            if len(API_processed_messages) == 0:
                return
            else:
                print('generating message')

                message = await self.API_processed_channel.fetch_message(API_processed_messages[0].id)
                for file in os.listdir(f"{self.path_ready}"):
                    if file.endswith(".png"):
                        
                        print('there is a file')
                        
                        path = os.path.join(f"{self.path_ready}", file)
                        try:
                            
                            os.remove(f"{self.program_path_back}Ready\{file}")
                        except OSError as e: # name the Exception `e`
                            print ("Failed with:", e.strerror )# look what it says
                            print ("Error code:", e.code )   
                for file in message.attachments:
                    if file.filename.endswith(".png") == True:
                        file_path = file
                        myfile = requests.get(file_path)
                        with open(f"{self.path_ready}/{file.filename}", "wb") as outfile:
                            outfile.write(myfile.content)
                            outfile.close()
                files = []
                for file in os.listdir(f"{self.path_ready}"):
                    if file.endswith(".png"):
                        file_saved = discord.File(f'{self.path_ready}/{file}', filename=f"{file}")
                        files.append(file_saved)
                await message.delete()
                content = message.content
                content = str(content).replace("'", '"')
                content = str(content).replace("True", 'true')
                content = str(content).replace("False", 'false')
                data =  json.loads(content)
                await self.generate_message(data, files)
            

    @tasks.loop(minutes = 1)
    async def task_update_embed(self):
        date = datetime.datetime.now()
        stock = await self.get_API_processed_channel_length()
        print('stock', stock)
        screen_number = len(list(self.bot.db.get_all_found_colonies()))
        embed = discord.Embed(title='✅ Screened Colonies', description=f'📸 Screens remaining: `{stock}`\n🪐 Colonies screened so far: `{screen_number}`', timestamp=date)
        hist_list = [hist_list async for hist_list in self.ocr_channel.history(limit=10, oldest_first=False)]
        if_embed = False
        if len(hist_list) >= 1:
            for message in hist_list:
                if message.embeds != []:
                    if message.embeds[0].title[0] == "✅":
                        await message.edit(embed=embed)
                        if_embed = True
            if if_embed == False:
                await self.ocr_channel.send(embed=embed)
        
    @task_update_embed.before_loop
    async def before_task_update_embed(self):
        await self.bot.wait_until_ready()
        
    @task_writing_coords.before_loop
    async def before_task_writing_coords(self):
        await self.bot.wait_until_ready()
            
    async def get_API_processed_channel_length(self):
        channel = self.API_processed_channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
        return count
    
    async def generate_message(self, data, files):
        self.skip = False
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
            self.skip == True
            await self.store_colonies(data)
        
        print('sending message', self.skip)
        
        if self.skip == False:
            files.reverse()
            view = await self.add_menu(data, view, content)
            view = await self.add_button(data, view, content)
            await self.ocr_channel.send(content=content, view=view, files=files)
    
    async def add_menu(self, data, view, content):
        for it_player in range(0, len(data['Players'])):
            if  data['Players'][it_player] in data["Proposal"]:
                await self.menu(data, view, it_player, content)
                data["Menu_number"] += 1
        return (view)

    async def button_write_name(self, view, data, it_player, content): 
        button_write_name = Button(label = f"{data['Players'][it_player]}", style=discord.ButtonStyle.grey)  
        view.add_item(button_write_name)
        async def button_callback_write_name(interaction):
            test_name_1 = data['Players'][it_player]
            class my_modal(ui.Modal, title='Add username'):
                player=ui.TextInput(label='username', style=discord.TextStyle.short, default=f'{test_name_1}', required = True)   
                async def on_submit(self_2, interaction):
                    for player_index in range(0, len(data["No_Result"])):
                        if data["No_Result"][player_index] == test_name_1:
                            child_number = player_index
                            data["No_Result"].append(self_2.player.value)
                            del data["No_Result"][player_index]
                            break
                    test_name = data['Players'][it_player]
                    results = requests.get(f'https://api.galaxylifegame.net/Users/name?name={self_2.player.value}', timeout=1.5)
                    if chr(results.content[0]) == '{':  
                        button_write_name = Button(label = f"{self_2.player.value}", style=discord.ButtonStyle.green)
                        view.remove_item(view.children[child_number+data["Menu_number"]])
                        view.add_item(button_write_name)
                        for index in range(0, len(data["Players"])):
                            if data["Players"][index] == test_name:
                                data['Players'][index] = self_2.player.value
                                data['Ready_to_store'][index] = True
                    else:
                        for index in range(0, len(data["Players"])):
                            if data["Players"][index] == test_name:
                                data['Players'][index] = self_2.player.value
                                data['Ready_to_store'][index] = False
                                break
                        view.remove_item(view.children[child_number+data["Menu_number"]])
                        button_write_name = Button(label = f"{self_2.player.value}", style=discord.ButtonStyle.red) 
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
                        await self.store_colonies(data)
            await interaction.response.send_modal(my_modal())
        button_write_name.callback = button_callback_write_name  
        
        
    
    async def menu(self, data, view, it_player, content):
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
                            await self.store_colonies(data)
                    else:
                        for it in range(0, len(data['Proposal'])):
                            if  data['Players'][it_player] in data["Proposal"]:
                                view.remove_item(view.children[it])
                                await self.button_write_name(view, data, it_player, content)  
                                data["No_Result"].append(data['Players'][it_player])
                                data["Menu_number"] -= 1
                                await interaction.response.edit_message(view=view)
                                break
        select.callback = my_callback
        
        
    async def add_button(self, data, view, content):
        for it_player in range(0, len(data['Players'])):
            
            if data['Players'][it_player] in data["No_Result"]:
                await self.button_write_name(view, data, it_player, content)
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

    # def get_screen(data):
    #     filename = f"{data['Location'][0]}_{data['Location'][1]}.png"
    #     file = discord.File(f"{bot.path}/{filename}", filename=filename)
    #     return file


    def db_handle(self, data):
        for player in data['Players']:
            player_infos = self.bot.galaxyLifeAPI.get_player_infos_from_name(player)
            player_id = player_infos['player_id_gl']        
            print(f"attempting to store colony:  {player} ({player_id}): {data['Title']}({data['Location']})")
            colony: Found_Colony_Model = {'gl_id': player_id, 'colo_sys_name':data['Title'], 'X': int(data['Location'][0]), 'Y':int(data['Location'][1])}
            self.bot.db.push_found_colony(colony)
            
    async def store_colonies(self, data):
        content = ""
        self.skip = True
        for player in data['Players']:
            content += f"**{player}**: {data['Location'][0]} : {data['Location'][1]}\n"

            async for message in self.ocr_channel.history(limit=10):
                coord_x = []
                coord_y = []
                coord_x.append([m.start() for m in re.finditer(f"{data['Location'][0]}", message.content)])
                coord_y.append([m.start() for m in re.finditer(f"{data['Location'][1]}", message.content)])
                if coord_x != [[]] and coord_y != [[]]:
                    await message.delete()
                    
        thread_store_colonies: Thread = Thread(target=self.db_handle, args=(data,))
        thread_store_colonies.daemon = True
        thread_store_colonies.start()
        

        



    
async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_Writing_Coords(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])