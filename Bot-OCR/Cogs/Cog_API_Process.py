import asyncio
import datetime
import itertools
import json
import os
import re
import time
from collections import Counter

import discord
import requests
from config.definitions import ROOT_DIR
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, Select, View
from Models.Found_Colony_Model import Found_Colony_Model


class Cog_API_Process(commands.Cog):
    bot: commands.Bot = None

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.username_count = 0
        self.success_count = 0
        self.multiple_answer_count = 0
        self.fail = 0
        self.matching_list = []
        self.program_path_back_processed = os.path.join(ROOT_DIR, 'Processed')
        self.program_path = os.path.join(ROOT_DIR)
        self.path = os.path.join(ROOT_DIR, 'Processed')
        self.path_unprocessed = os.path.join(ROOT_DIR, 'Unprocessed')
        self.processed_channel_id = int(os.getenv("PROCESSED_CHANNEL"))
        self.processed_channel = self.bot.get_channel(self.processed_channel_id)
        self.API_processed_channel_id = int(os.getenv("API_PROCESSED_CHANNEL"))
        self.API_processed_channel = self.bot.get_channel(self.API_processed_channel_id)
        self.worked_first_try = False
        self.api_process_messages.start()
    
    @tasks.loop(seconds = 1)
    async def api_process_messages(self):
        await self.process()

    @api_process_messages.before_loop
    async def before_api_process_messages(self):
        await self.bot.wait_until_ready()
     
    async def process(self):
        self.matching_list = []
        self.data = await self.get_data()
        if self.data is None:
            return
        print(self.data)
        if self.data['Title'] == "-1" or self.data['Title'] == None:
            self.data['Title'] = "Unknown System"
        else:
            self.data["Title"], anything = self.preprocess(self.data["Title"])
        self.user_list = []
        for player in self.data['PlanetInfos']:
            print(player)
            if player['PlayerName'] != "" and len(player['PlayerName']) >= 3:
                self.user_list.append(player['PlayerName'])
                print('appending')
        print(self.user_list)
        # if self.user_list == []:
        #     print("the user list is empty !!!")
        
        self.data = {'Title': self.data['Title'], 'Location': self.data['Location']}
        self.data['Proposal'] = {}
        self.data['No_Result'] = []
        self.data['Ready_to_store'] = []
        self.data['Menu_number'] = 0
        self.data['Button_number'] = 0
        index = 0
        for word in self.user_list:
            if len(word) > 12:
                while len(word) > 12:
                    word = word[1:]
                    word = word[:len(word)-1]
                self.user_list[index] = word
            if len(word) < 4:
                del self.user_list[index]
            index += 1
        self.user_list = list(dict.fromkeys(self.user_list))
        self.data['Players'] = []
        for it in self.user_list:
            self.data['Players'].append("player")
        for it in range(0, len(self.data["Players"])):
            self.data['Ready_to_store'].append(False)
        print(self.user_list)
        self.OCR_sender()   
        print('everything all done')
        files =  []
        files_ends = ["Processing_worthy", "Processing_players0" ]
        for file in os.listdir(f"{self.path}"):
            if file.endswith("players1.png"):
                print('found extra file')
                files_ends.append("Processing_players1") 
        # print(files_ends)
        for file_end in files_ends:
            filename = f"{self.data['Location'][0]}_{self.data['Location'][1]}_{file_end}.png"
            try:
                # print('test', f"{os.path.join(ROOT_DIR, 'Processed', filename)}")
                files.append(discord.File(f"{os.path.join(ROOT_DIR, 'Processed', filename)}", filename=filename))
            except Exception as e:
                print ("Failed with:", e.strerror )  
        send_bool: bool = await self.check_sendability(self.data)
        print('sendability checked')
        if send_bool == True:
            await self.API_processed_channel.send(self.data, files=files)
        await self.clear_message()
        
    async def check_sendability(self, data):
        true_number: int = 0
        for it in range(0, len(data['Players'])):
            if data['Ready_to_store'][it] == True:
                true_number += 1
        if true_number == len(data["Players"]):
            print('✅✅✅ processed result was perfect')
            if 'DefiniteWrongLocation' in data:
                    if data['DefiniteWrongLocation'] == True:
                        print('⚠️ but coords are wrong. Seending instead.')
            elif data['Location'][0] == "-1" or data['Location'][1] == "-1":
                print('⚠️ but coords are wrong. Seending instead.')
            else:
                print('storage rules are matching')
                await self.db_handle(data)
                return False
        else: 
            return True
                
    async def db_handle(self, data):
        for player in data['Players']:
            player_infos = self.bot.galaxyLifeAPI.get_player_infos_from_name(player)
            player_id = player_infos['player_id_gl']        
            print(f"attempting to store colony:  {player} ({player_id}): {data['Title']}({data['Location']})")
            colony: Found_Colony_Model = {'gl_id': player_id, 'colo_sys_name':data['Title'], 'X': int(data['Location'][0]), 'Y':int(data['Location'][1])}
            self.bot.db.push_found_colony(colony)
        
    async def get_data(self):
        it_message = 0
        history = self.processed_channel.history(oldest_first=True, limit=1)
        hist_list = [hist_list async for hist_list in self.processed_channel.history(limit=1, oldest_first=False)]
        print("[Info]: New Iteration")
        for file in os.listdir(f"{os.path.join(ROOT_DIR, 'Processed')}"):
            if file.endswith(".png"):
                try:
                    os.remove(f"{os.path.join(ROOT_DIR, 'Processed', file)}")
                except OSError as e:
                    print ("Failed with:", e.strerror )
        if hist_list != []:
            for message in hist_list:
                it = 0
                data =  json.loads(message.content)
                for attachment in message.attachments:
                    if attachment.filename.endswith(".png") == True:
                        file_path = attachment
                        myfile = requests.get(file_path)
                        screen_name = str(data['Location']).split(', ')
                        with open(f"{os.path.join(ROOT_DIR, 'Processed', f'{screen_name[0]}_{screen_name[1]}_{attachment.filename}')}", "wb") as outfile:
                            outfile.write(myfile.content)
                        it += 1    
                    it_message += 1 
                # await message.delete()
        else:
            return None
        return data
    
    async def clear_message(self):
        
        hist_list = [hist_list async for hist_list in self.processed_channel.history(limit=1, oldest_first=False)]
        if hist_list != []:
            for message in hist_list:
                print('clearing message in processed channel')
                await message.delete()
    
    def preprocess(self, player_input):
        player_input = player_input.replace("/N", "M")
        player_input = player_input.replace("//", "M")
        player_input = player_input.replace("?", "7")
        player_input = player_input.replace("_", "")
        player_input = player_input.replace("\\", "")
        player_input = player_input.replace("/", "")
        player_input = player_input.replace("€", "E")
        player_input = player_input.replace("&", "E")
        player_input = player_input.replace("§", "6")
        player_input = player_input.replace(":", "3")
        player_input = player_input.replace(",", "")
        
        chr = "\ "
        player_input = player_input.replace(f'{chr[0]}', "1")
        player_input = player_input.replace("(", "O")
        player_input = player_input.replace(")", "1") 
        player_input = player_input.replace("!", "1")   
        player_input = player_input.replace("^", "A")
        player_input = player_input.replace(",", "")
        
        player_input = player_input.replace("«s>", "")
        player_input = player_input.replace("«s»", "")
        player_input = player_input.replace("<s>", "")
        player_input = player_input.replace("«", "")
        player_input = player_input.replace("<", "")
        player_input = player_input.replace(">", "")
        player_input = player_input.replace("_", "")    
        player_input = player_input.replace("'", "")
        player_input = player_input.replace('"', "")
        player_input = player_input.replace(".", "")
        player_input = player_input.replace("|", "")
        player_input = player_input.replace("}", "")
        player_input = player_input.replace(";", "")
        player_input = player_input.replace("¢", "")
        player_input = player_input.replace("°", "")
        player_input = player_input.replace("¡", "")
        player_input = player_input.replace("к", "k")
        player_input = player_input.replace("#", "")
        player_input = player_input.replace("[", "")
        player_input = player_input.replace(",", "")
        player_input = player_input.replace("=", "3")
        player_input = player_input.replace("е", "e")
        player_input = player_input.replace("м", "m")
        player_input = player_input.replace("у", "y")
        
        player_input = player_input.replace("т", "t")
        player_input = player_input.replace("о", "o")
        player_input = player_input.replace("р", "p")
        player_input = player_input.replace("д", "a")
        player_input = player_input.replace("с", "c")
        player_input = player_input.replace("л", "n")
        
        
        

        print("pre processed string:", player_input)
        username_list = [player_input]
        return player_input, username_list


    def filter(self, player_input):
        char_found_index = []
        # Q -> 4
        # N -> M
        # VV -> W
        # +++ U -> LI
        char_found_index.append([m.start() for m in re.finditer('3', player_input)]) # 3 -> B
        char_found_index.append([m.start() for m in re.finditer('s', player_input)]) # S -> B
        char_found_index.append([m.start() for m in re.finditer('b', player_input)]) # B -> 3
        
        char_found_index.append([m.start() for m in re.finditer('o', player_input)]) # O -> 0
        char_found_index.append([m.start() for m in re.finditer('0', player_input)]) # 0 -> O
        
        char_found_index.append([m.start() for m in re.finditer('z', player_input)]) # Z -> 2
        char_found_index.append([m.start() for m in re.finditer('2', player_input)]) # 2 -> Z
        
        char_found_index.append([m.start() for m in re.finditer('s', player_input)]) # S -> 5
        char_found_index.append([m.start() for m in re.finditer('5', player_input)]) # 5 -> S
        
        char_found_index.append([m.start() for m in re.finditer('11', player_input)]) # 11 -> N
        char_found_index.append([m.start() for m in re.finditer('a', player_input)]) # A -> 4
        
        char_found_index.append([m.start() for m in re.finditer('e', player_input)]) # E -> S
        char_found_index.append([m.start() for m in re.finditer('s', player_input)]) # S -> E
        
        char_found_index.append([m.start() for m in re.finditer('s', player_input)]) # S -> 8
        
        
        char_found_index.append([m.start() for m in re.finditer('n', player_input)]) # N -> M
        char_found_index.append([m.start() for m in re.finditer('i', player_input)]) # I -> 1
        char_found_index.append([m.start() for m in re.finditer('i', player_input)]) # I -> T
        

        replace_chr: list = ["3", "s", "b", "o", "0", "z", "2", "s", "5", "11", "a", "e", "s", "s", "n", "i", "i"] 
        original_chr: list = ["b", "b", "3", "0", "o", "2", "z", "5", "s", "n", "4", "s", "e", "8", "m", "1", "t"] 
        return char_found_index, original_chr, replace_chr

    # it_char_found : position in list of replacement chars 
    # char_found_index: position of the found char: list
    # index : x value of char_found_index
    # swap : all combinaisons of char for all chars 
    # x_char_in_swap : all combinaisons for 1 char
    # x_char_in_swap_index : one combinaison for 1 char

    def username_builder(self, char_found_index, original_chr, replace_chr, player_input, username_list):
        it_char_found = 0
        it = 0 
        for index in char_found_index:
            swap = []
            for L in range(len(char_found_index[it_char_found]) + 1):
                for subset in itertools.combinations(index, L):
                    swap.append(subset)
            for x_char_in_swap in swap:
                if len(x_char_in_swap) > 0:
                    result_it = player_input
                    for x_char_in_swap_index in x_char_in_swap:
                        result_it = result_it[:x_char_in_swap_index] + original_chr[it_char_found] + result_it[x_char_in_swap_index+len(replace_chr[it_char_found]):]
                        it += 1
                    username_list.append(result_it)
            it_char_found += 1
        return username_list

    def api_check(self, username_list):
        self.worked_first_try = False
        given_results = []
        username_list = username_list [0:10]
        try:
            results = requests.get(f'https://api.galaxylifegame.net/Users/name?name={username_list[0]}', timeout=5.0)
            # for it in range(0, 15):
            #     print(chr(results.content[it]))
        except Exception as e:
            print(e)
            results = []
            
        if chr(results.content[0]) == '{':  
            results = json.loads(results.content)
            if results != []:
                print('✅ worked at 1st try', results)
                self.worked_first_try = True
                results = [[(f"{results['Name']}")]]
                self.data['Players'][self.it] = str(results)[3:-3]
                return results
        for it in range(0, len(username_list)):
            resulting_name: bool = False
            while resulting_name == False:
                try:
                    results = requests.get(f'https://api.galaxylifegame.net/Users/name?name={username_list[it].lower()}', timeout=5.0)
                    results = json.loads(results.content)
                    if results == []:
                        results = requests.get(f'https://api.galaxylifegame.net/Users/name?name={username_list[it].upper()}', timeout=5.0)
                        results = json.loads(results.content)
                    # for it in range(0, 15): 
                    #     print(chr(results.content[it]))
                except Exception as e:
                    results = []
                if results != []:
                    names = []
                    if 'Id' in results:
                        names.append(results['Name'])
                    else:
                        for player in results:
                            names.append(player['Name'])
                    given_results.append(names)
                    resulting_name = True
                else:
                    resulting_name = True
                    # if len(username_list[it]) > 8:
                    #     username_list[it] = username_list[it][:-1]
                    #     # print(username_list[it])
                    # else:
                    #     resulting_name = True
        # print("Results for all variations :", given_results)
        return given_results
        
    def exhaustive_usernames(self, char_found_index, original_chr, replace_chr, username_list):
        username_list_exh: list = []
        username_list_flat: list = []
        for it in range(0, len(username_list)):
            username_list_exh.append(self.username_builder(char_found_index, original_chr, replace_chr, username_list[it], username_list))
        for list_index in range(0, len(username_list_exh)):
            for index in range(0, len(username_list_exh[list_index])):
                username_list_flat.append(username_list_exh[list_index][index])
        final_username_list = list(dict.fromkeys(username_list_flat))
        # print("variants:", len(final_username_list))
        if len(final_username_list) > 25:
            #print("variants number was:", len(final_username_list))
            final_username_list = final_username_list[0]
            #print(final_username_list)
        return final_username_list


    def most_frequent(self, List):
        if List != []:
            most_common = [item for item in Counter(List).most_common()]
            return str(most_common[0:10])
        else:
            return 'No most frequent result found'
        
    def test_username(self, player_input, username_list):  
        given_results = []
        char_found_index, original_chr, replace_chr = self.filter(player_input)
        username_list = username_list[0:4]
        username_list_2 = self.username_builder(char_found_index, original_chr, replace_chr, player_input, username_list)
        # print("🔎 variants that won't be used:", username_list_2, "vs", username_list)
        # username_list_3 = self.exhaustive_usernames(char_found_index, original_chr, replace_chr, username_list)
        # print("🔎 variants that won't be used:", username_list_3)
        given_results = self.api_check(username_list)
        given_results_done = []
        for list_index in range(0, len(given_results)):
            for index in range(0, len(given_results[list_index])):
                given_results_done.append(given_results[list_index][index])
                
        if given_results_done == []:
            print('no result')
            return None
        # print("Usernames returned by API :", given_results) 
        matching_name = self.most_frequent(given_results_done)
        print("Most frequent username from API:", matching_name , "\n")
        return matching_name


    def OCR_sender(self):
        time_start: datetime.datetime = datetime.datetime.now() 
        self.it = 0
        for user in self.user_list:
            self.username_count += 1
            user, username_list = self.preprocess(user)
            self.data["Players"][self.it] = user
            if user != "":
                not_decreased = True
                result = self.test_username(user, username_list)
                while result == None:
                    if len(user) > 4:
                        #print("decreasing size")
                        not_decreased = False
                        user = user[1:]
                        user = user[:len(user)-1]
                        username_list = [user]
                        result = self.test_username(user, username_list)
                    else:
                        result = "No result Found"
                        user, username_list = self.preprocess(self.user_list[self.it])
                        self.data['No_Result'].append(user) 
                        self.fail += 1
                        self.matching_list.append(result)
                
                if result != 'No result Found':
                    elements: int = 0
                    for chr in result:
                        if chr == '(':
                            elements += 1
                    if elements == 1 and self.worked_first_try == True and not_decreased == True:
                        self.matching_list.append(result)
                        print('✅ worked first try is true')
                        self.user_list[self.it] = result
                        self.success_count += 1
                    elif elements == 1 and self.worked_first_try == True and not_decreased == False:
                        print('❌ one result but username got decreased in size')
                        self.matching_list.append(result)
                        if len(self.data['Proposal']) < 5:
                            result = list(result.split("'"))
                            result_list = []
                            for proposal in range(0, len(result)):
                                if proposal %2 == 1:
                                    result[proposal] = result[proposal]
                                    result_list.append(result[proposal])
                            self.data["Proposal"][f'{self.data["Players"][self.it]}'] = result_list
                        else:
                            print("👄👄👄👄 too many menus. adding it as no_result")
                            self.data['No_Result'].append(self.data["Players"][self.it])
                            print(self.data)
                            
                    elif elements == 1 and self.worked_first_try == False:
                        print('❌ one result but didnt work at first try')
                        self.matching_list.append(result)
                        if len(self.data['Proposal']) < 5:
                            result = list(result.split("'"))
                            result_list = []    
                            for proposal in range(0, len(result)):
                                print(proposal)
                                print(result)
                                if proposal %2 == 1:
                                    print(result[proposal])
                                    result[proposal] = result[proposal]
                                    result_list.append(result[proposal])
                            self.data["Proposal"][f'{self.data["Players"][self.it]}'] = result_list
                        else:
                            print("👄👄👄👄 too many menus. adding it as no_result")
                            self.data['No_Result'].append(self.data["Players"][self.it])
                            print(self.data)
                    
                    elif elements > 1:
                        self.multiple_answer_count += 1
                        print(result)
                        
                        if len(self.data['Proposal']) < 5:
                            result_splitted = list(result.split("'"))
                            result_list = []
                            for proposal in range(0, len(result_splitted)):
                                if proposal %2 == 1:
                                    result_splitted[proposal] = result_splitted[proposal]
                                    result_list.append(result_splitted[proposal])
                            self.data["Proposal"][f'{self.data["Players"][self.it]}'] = result_list
                        else:
                            print("👄👄👄👄 too many menus. adding it as no_result")
                            result = "No result Found"
                            self.data['No_Result'].append(self.data["Players"][self.it])
                            print(self.data)
                        self.matching_list.append(result)
                        print('5')
            else:
                print('❌ No result found because there was no name')
                result = "No result Found"
                self.matching_list.append(result)
                self.data["Players"][self.it] = "No Name"
                self.data['No_Result'].append("No Name") 
                self.fail += 1
            self.it += 1
        print('6')
        time_end: datetime.datetime = datetime.datetime.now()
        # print(f'program executed for {time_end - time_start} ')
        # print('usernames', self.username_count)
        # print('success:', self.success_count)
        # print('multiple answer:', self.multiple_answer_count)
        # print('fail:', self.fail)
        location = self.data["Location"].replace(" ", "")
        location_list = list(location.split(","))
        self.data["Location"] = location_list
        it = 0
        print('did it change? we"ll see:', self.data['Players'])
        for name in range(0, len(self.data['Players'])):
            accurate_name = str(self.matching_list[name]).split("'")
            
            if not self.data['Players'][name] in self.data['Proposal'] and self.matching_list[name] != 'No result Found':
                print(self.data['Players'][name], "---->", accurate_name[1], "\n")
                self.data['Ready_to_store'][it] = True
                self.data['Players'][it] = accurate_name[1]
            elif self.matching_list[name] == 'No result Found':
                print(self.data['Players'][name], "---->", self.matching_list[name], "\n")
            else:
                print(self.data['Players'][name], "---->", self.data['Proposal'][self.data['Players'][name]], "\n")
            it += 1
        print(self.data)    

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog_API_Process(bot), guilds=[discord.Object(id=os.getenv("SERVER_ID"))])