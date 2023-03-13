import discord
import json
import requests

class GalaxyLifeAPI:
    url: str 
    
    def __init__(self):
        self.url = "https://api.galaxylifegame.net"
    
    def get_emblem(self, shape: str, pattern: str, icon: str) -> str:
        return f"https://cdn.galaxylifegame.net/content/img/alliance_flag/AllianceLogos/flag_{shape}_{pattern}_{icon}.png"
      
    def get_request(self, url: str) -> Any:
        response = requests.get(url, timeout = 2.50)
        if response.status_code != 200:
            return None
        if response.content[0] != "{":   
            return None
        else: 
            return json.loads(response.content)    
    
    def get_alliance(self, alliance: str) ->  Any:
        return_value: dict = {}
        url: str = self.url + f"/alliances/get?name={alliance}"
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
    
    def get_player_infos(self, player_id):
        return_value: dict = {}
        url = self.url + f"/Users/get?id={player_id}"
        player_infos = self.get_request(url)
        return_value["mb_lvl"] = player_infos['Planets'][0]['HQLevel']
        return_value["player_lvl"] = player_infos['Level']
        return_value["colo_list"] = []
        player_infos['Planets'] = player_infos['Planets'][1:len(player_infos['Planets'])] 
        for colo in player_infos['Planets']:
            return_value["colo_list"].append(player_infos['Planets'][colo]['HQLevel'])
        return None    
        
    def get_player_steam_ID(self, player_id):
        url: str = self.url + f"/Users/platformId?userId={player_id}"
        return self.get_request(url)
        