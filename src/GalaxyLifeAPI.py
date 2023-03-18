import discord
import json
import requests
import os

class GalaxyLifeAPI:
    url_gl: str 
    steamToken: str
    
    def __init__(self):
        self.url_gl = "https://api.galaxylifegame.net"
        self.steamToken = os.getenv("STEAM_TOKEN")
        self.url_steam = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2"
    
    def get_emblem(self, shape: str, pattern: str, icon: str) -> str:
        return f"https://cdn.galaxylifegame.net/content/img/alliance_flag/AllianceLogos/flag_{shape}_{pattern}_{icon}.png"
      
    def get_request(self, url: str):
        response: str = requests.get(url, timeout = 2.50)
        if response.status_code != 200:
            return None
        if chr(response.content[0]) != "{" and chr(response.content[1]).isdigit() != True:  
            return None 
        else: 
            return json.loads(response.content)    
    
    def get_alliance(self, alliance: str):
        return_value: dict = {}
        url: str = self.url_gl + f"/Alliances/get?name={alliance}"
        alliance_infos = self.get_request(url)
        if alliance_infos == None:
            return None
        return_value["alliance_lvl"] = alliance_infos['AllianceLevel']
        return_value["alliance_size"] =  len(alliance_infos['Members'])
        return_value["emblem_url"] = self.get_emblem(alliance_infos['Emblem']['Shape'], alliance_infos['Emblem']['Pattern'], alliance_infos['Emblem']['Icon'])   
        return_value["members_list"] = []
        for member in alliance_infos['Members']:
            return_value["members_list"].append({"Name": member["Name"], "Id": member["Id"]})
            
        if alliance_infos['WarsWon'] != 0 and alliance_infos['WarsLost'] != 0:
            return_value["alliance_winrate"] = round(alliance_infos['WarsWon'] / (alliance_infos['WarsLost'] + alliance_infos['WarsWon']) * 100, 2)
        else:
            return_value["alliance_winrate"] = -1
        return return_value    
 
    def get_player_infos_from_name(self, player_name):
        return_value: dict = {}
        url: str = self.url_gl + f"/Users/name?name={player_name}"
        player_infos = self.get_request(url)
        return_value["mb_lvl"] = player_infos['Planets'][0]['HQLevel']
        return_value["player_lvl"] = player_infos['Level']
        if player_infos['AllianceId'] != None:
            return_value["alliance_name"] = player_infos['AllianceId'].upper()
        else:
            return_value["alliance_name"] = None
        return_value["colo_list"] = []
        return_value["player_id_gl"] = player_infos['Id']
        return_value["avatar_url"] = player_infos['Avatar']
        player_infos['Planets'] = player_infos['Planets'][1:len(player_infos['Planets'])] 
        it: int = 0
        for colonies in player_infos['Planets']:
            return_value["colo_list"].append(player_infos['Planets'][it]['HQLevel'])
            if it == len(player_infos['Planets']):
                break
            it = it + 1

        return return_value    
        
    
    def get_player_infos(self, player_id):
        return_value: dict = {}
        url: str = self.url_gl + f"/Users/get?id={player_id}"
        player_infos = self.get_request(url)
        return_value["mb_lvl"] = player_infos['Planets'][0]['HQLevel']
        return_value["player_lvl"] = player_infos['Level']
        return_value["colo_list"] = []
        player_infos['Planets'] = player_infos['Planets'][1:len(player_infos['Planets'])] 
        it: int = 0
        for colonies in player_infos['Planets']:
            return_value["colo_list"].append(player_infos['Planets'][it]['HQLevel'])
            if it == len(player_infos['Planets']):
                break
            it = it + 1

        return return_value    
        
    def get_player_steam_ID(self, player_id_gl):
        url: str = self.url_gl + f"/Users/platformId?userId={player_id_gl}"
        return self.get_request(url)
       
    def get_steam_url(self, player_id_gl):
        player_id_steam: str = self.get_player_steam_ID(player_id_gl)
        url: str = self.url_steam + f'/?key={self.steamToken}&format=json&steamids={player_id_steam}'
        response_info: str = requests.get(url)
        response_parse: dict = json.loads(response_info.content)
        return response_parse["response"]["players"][0]["profileurl"]
    
    def get_player_status(self, player_id_gl):
        player_id_steam: str = self.get_player_steam_ID(player_id_gl)
        url: str = self.url_steam + f'/?key={self.steamToken}&format=json&steamids={player_id_steam}'
        response_info: str = requests.get(url)
        #response_info.raise_for_status() 
        if response_info.status_code != 204 and response_info.status_code != 500:   
            response_parse: dict = json.loads(response_info.content)
            if len(response_parse['response']['players'][0]) >= 1:
                if response_parse['response']['players'][0]['personastate'] == 1:
                    if "gameextrainfo" in response_parse['response']['players'][0]:
                        if response_parse['response']['players'][0]['gameextrainfo'] == "Galaxy Life": 
                           # print('player online')   
                            return 1
        return 0