import datetime
import itertools
import json
import re
from collections import Counter
import os
import requests

# player_input = "MYSNCCCCC"

class OCR_API:

    def __init__(self):
        self.username_count = 0
        self.success_count = 0
        self.multiple_answer_count = 0
        self.fail = 0
        self.matching_list = []
        self.path_unprocessed = "Bot-OCR\\Unprocessed"
        self.path_processed = "Bot-OCR\\Processed"
        for file in os.listdir(self.path_unprocessed):
            if file.endswith(".json"):
                break
        with open(f'{self.path_unprocessed}\{file}') as fp:
                self.data = json.load(fp)
        # "SLAY","2ITOO","SEBAKING33","/NATIXEU","1","YHORDANPERZ019","MNOJOREK", "OIRIAURE","ELDEREKDIMITRY","NATATEK",
        #,"JOHNNY","DICTUMN","HUGO12345","BRODERTUCK","BROZ2DI","1","YUJIROTHEOGRE","21737215","JOHNYKO!", "SZNEJKS","SErGIOIZGOT","MANLEY","AMARUXXGR","FELLOWJITSTER","HERCIO","1","ARGENTINAPAPASNDIGUERREIRC", "MNASTGOL","COUTIETJ","QRTHXR","TDDMEATHOOK","SHAFUL","kaspianziomAal","|","MAGASKILLLS","~~","ALBEN\\ONA","VVALENIN","30n030200", "goz2l4az20","ROBER289","CARLOSS5582","SANILEPUNCHS)!","GIGAMIN","MAGASKILLLS", "WNICOS","SAHIANACORDOBA","ZZ2PIPEEENNISSBUNBLEBEESC","/VIATIANA","RUINMTETROTTER"
        self.user_list = self.data["Players"]
        self.data['Proposal'] = {}
        self.data['No_Result'] = []
        self.data['Ready_to_store'] = []
        self.data['Menu_number'] = 0
        index = 0
        for word in self.user_list:
            if len(word) > 10:
                while len(word) > 10:
                    word = word[1:]
                    word = word[:len(word)-1]
                print(word)
                self.user_list[index] = word
            if len(word) < 4:
                del self.user_list[index]
            index += 1
        self.user_list = list(dict.fromkeys(self.user_list))
        self.data['Players'] = []
        for it in self.user_list:
            self.data['Players'].append("player")
        print(self.data)
        for it in range(0, len(self.data["Players"])):
            self.data['Ready_to_store'].append(False)
        print("len players", it)
        print(self.user_list)
        print(len(self.user_list))
        self.OCR_sender()   
        
    def preprocess(self, player_input):
        player_input = player_input.replace("/N", "M")
        player_input = player_input.replace("//", "M")
        player_input = player_input.replace("?", "7")
        player_input = player_input.replace("_", "")
        player_input = player_input.replace("\\", "")
        player_input = player_input.replace("€", "E")
        player_input = player_input.replace(":", "3")
        print("pre processed username:", player_input)
        username_list = [player_input]
        return player_input, username_list


    def filter(self, player_input):
        char_found_index = []
        # Q -> 4
        # N -> M
        # VV -> W
        char_found_index.append([m.start() for m in re.finditer('3', player_input)]) # 3 -> B
        char_found_index.append([m.start() for m in re.finditer('S', player_input)]) # S -> B
        char_found_index.append([m.start() for m in re.finditer('B', player_input)]) # B -> 3
        
        char_found_index.append([m.start() for m in re.finditer('NN', player_input)]) # NN -> M
        char_found_index.append([m.start() for m in re.finditer('MN', player_input)]) # MN -> M
        char_found_index.append([m.start() for m in re.finditer('AM', player_input)]) # AM -> M
        
        char_found_index.append([m.start() for m in re.finditer('N', player_input)]) # N -> T1
        
        char_found_index.append([m.start() for m in re.finditer('UW', player_input)]) # UW -> W
        char_found_index.append([m.start() for m in re.finditer('WW', player_input)]) # WW -> W
        
        char_found_index.append([m.start() for m in re.finditer('Z', player_input)]) # Z -> 2
        char_found_index.append([m.start() for m in re.finditer('2', player_input)]) # 2 -> Z
        char_found_index.append([m.start() for m in re.finditer('Z2', player_input)]) # Z2 -> Z
        
        char_found_index.append([m.start() for m in re.finditer('S', player_input)]) # S -> 5
        char_found_index.append([m.start() for m in re.finditer('5', player_input)]) # 5 -> S
        
        char_found_index.append([m.start() for m in re.finditer('O', player_input)]) # O -> 0
        char_found_index.append([m.start() for m in re.finditer('0', player_input)]) # 0 -> O
        
        char_found_index.append([m.start() for m in re.finditer('Y', player_input)]) # Y -> 1
        char_found_index.append([m.start() for m in re.finditer('1', player_input)]) # 1 -> Y
        
        char_found_index.append([m.start() for m in re.finditer('N', player_input)]) # N -> M
        char_found_index.append([m.start() for m in re.finditer('N', player_input)]) # N -> A
        char_found_index.append([m.start() for m in re.finditer('I', player_input)]) # I -> 1

        replace_chr: list = ["3", "S", "B", "NN", "MN", "AM", "N", "UW", "WW", "Z", "2", "Z2", "S", "5", "O", "0", "Y", "1", "N", "N", "I"] 
        original_chr: list = ["B", "B", "3", "M", "M", "M", "T1", "W", "W", "2", "Z", "Z", "5", "S", "0", "O", "1", "Y", "M", "A", "1"] 
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
            # print(swap)
            for x_char_in_swap in swap:
                # print(x_char_in_swap)
                if len(x_char_in_swap) > 0:
                    result_it = player_input
                    for x_char_in_swap_index in x_char_in_swap:
                        result_it = result_it[:x_char_in_swap_index] + original_chr[it_char_found] + result_it[x_char_in_swap_index+len(replace_chr[it_char_found]):]
                        # print(result_it)
                        it += 1
                    username_list.append(result_it)
            it_char_found += 1
        return username_list

    def api_check(self, username_list):
        given_results = []
        username_list = username_list [0:10]
        results = requests.get(f'https://api.galaxylifegame.net/Users/name?name={username_list[0]}', timeout=15.0)
        if chr(results.content[0]) == '{':  
            print(chr(results.content[0]))
            results = json.loads(results.content)
            if results != []:
                print('worked at 1st try')
                results = [[(f"{results['Name']}")]]
                self.data['Players'][self.it] = str(results)[3:-3]
                print(results)
                return results
        for it in range(0, len(username_list)):
            resulting_name: bool = False
            while resulting_name == False:
                results = requests.get(f'https://api.galaxylifegame.net/Users/search?name={username_list[it]}', timeout=15.0)
                results = json.loads(results.content)
                if results != []:
                    names = []
                    for player in results:
                        names.append(player['Name'])
                    given_results.append(names)
                    # print(names)
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
            print("variants number was:", len(final_username_list))
            final_username_list = final_username_list[0]
            print(final_username_list)
        return final_username_list


    def most_frequent(self, List):
        if List != []:
            most_common = [item for item in Counter(List).most_common()]
            # print (str(most_common))
            return str(most_common[0:25])
        else:
            return 'No result found'
        
    def test_username(self, player_input, username_list):  
        
        given_results = []
        char_found_index, original_chr, replace_chr = self.filter(player_input)
        # username_list = username_builder(char_found_index, original_chr, replace_chr, player_input, username_list)
        
        username_list = username_list[0:4]
        # print(username_list)
        username_list_2 = self.exhaustive_usernames(char_found_index, original_chr, replace_chr, username_list)
        given_results = self.api_check(username_list)

        given_results_done = []
        for list_index in range(0, len(given_results)):
            for index in range(0, len(given_results[list_index])):
                given_results_done.append(given_results[list_index][index])
                
        if given_results_done == []:
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
            result = self.test_username(user, username_list)
            while result == None:
                if len(user) > 4:
                    print("decreasing size")
                    user = user[1:]
                    user = user[:len(user)-1]
                    username_list = [user]
                    result = self.test_username(user, username_list)
                else:
                    print('No result found')
                    result = "No result Found"
                    self.data['No_Result'].append(self.user_list[self.it]) 
                    self.fail += 1
            
            self.matching_list.append(result)
            print("print", result, len(result))
            if result != 'No result Found':
                elements: int = 0
                for chr in result:
                    if chr == '(':
                        elements += 1
                if elements == 1:
                    self.user_list[self.it] = result
                    self.success_count += 1
                elif elements > 1:
                    self.multiple_answer_count += 1
                    result = list(result.split("'"))
                    print(result)
                    result_list = []
                    for proposal in range(0, len(result)):
                        if proposal %2 == 1:
                            result[proposal] = result[proposal]
                            print(result[proposal])
                            result_list.append(result[proposal])
                    self.data["Proposal"][f'{self.user_list[self.it]}'] = result_list
                    print(self.data["Proposal"])
                    # 
            self.it += 1

        # print(matching_list)
        time_end: datetime.datetime = datetime.datetime.now()
        print(f'program executed for {time_end - time_start} ')
        print('usernames', self.username_count)
        print('success:', self.success_count)
        print('multiple answer:', self.multiple_answer_count)
        print('fail:', self.fail)
        location = self.data["Location"].replace(" ", "")
        location_list = list(location.split(","))
        self.data["Location"] = location_list
        
        it = 0
        for name in range(0, len(self.data['Players'])):
            print(self.data['Players'][name], "---->", self.matching_list[name], "\n")
            if not self.data['Players'][name] in self.data['Proposal'] and self.matching_list[name] != 'No result Found':
                self.data['Ready_to_store'][it] = True
            it += 1
        print(self.data)        
        json_file = json.dumps(self.data, indent=1)
        
        with open(f"{self.path_processed}/{location_list[0]}_{location_list[1]}.json", "w") as outfile:
            outfile.write(json_file)
        os.remove(f"{self.path_unprocessed}\{location_list[0]}_{location_list[1]}.json")
    # ✅ take data from json
    # ✅ preprocess
    # ✅ generate variations
    # ✅ test each variation
    # ✅ if no result, decrease result size
    # ✅ if one result, replace name in data["Players"][it]
    # if multiple results, add to data['Proposal'] = {f'{data["Players"][it]}':[self.matching_list]}
    # think about how to handle No results
OCR_API()