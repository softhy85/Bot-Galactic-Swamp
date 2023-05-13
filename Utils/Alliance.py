import os
import datetime
from typing import List

import discord
from bson import ObjectId
from discord.ext import commands
from Models.Alliance_Model import Alliance_Model
from Models.Colony_Model import Colony_Model
from Models.Player_Model import Player_Model
from threading import Thread
import re

class Alliance:
    bot: commands.Bot = None
    command_channel_id: int = None
    command_channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.command_channel_id = int(os.getenv("COMMAND_CHANNEL"))
        self.command_channel = self.bot.get_channel(self.command_channel_id)

    async def add_alliance(self, alliance: str):
        api_alliance: dict = self.bot.galaxyLifeAPI.get_alliance(alliance)
        if api_alliance is None:
            # await self.command_channel.send(f"> {alliance} doesn't seem to exist on the API")
            return None
        else:
            new_alliance: Alliance_Model = {"name": alliance.upper(), "emblem_url":api_alliance["emblem_url"]}
            new_alliance["_id"] = self.bot.db.push_new_alliance(new_alliance)
            if new_alliance["_id"] is None:
                # await self.command_channel.send(f"> Something goes wrong while creating the Alliance {alliance}.\nPlease report this bug to @Softy(léo).")
                return None
            return new_alliance


    def update_colony_from_api(self, colo_nb: int, colo_level: int, alliance_id: int, db_player: Player_Model):
        date: datetime.datetime = datetime.datetime.now()
        updated_colony: Colony_Model = {"_alliance_id": alliance_id, 'id_gl': db_player["id_gl"], '_player_id': db_player["_id"], 'number': colo_nb, 'colo_sys_name': "?", 'colo_lvl': colo_level, 'colo_coord': {"x": -1, "y": -1}, 'colo_status': "Up", 'colo_last_attack_time': date, 'colo_refresh_time': date, 'updated': False, 'gift_state': "Not Free"}
        db_colony: List[Colony_Model] = list(self.bot.db.get_colonies({"_player_id": ObjectId(db_player["_id"]), "number": colo_nb}))
        if len(db_colony) == 1:
            updated_colony["_id"] = db_colony[0]["_id"]
            updated_colony["colo_sys_name"] = db_colony[0]["colo_sys_name"]
            updated_colony["colo_coord"]["x"] = int(db_colony[0]["colo_coord"]["x"])
            updated_colony["colo_coord"]["y"] = int(db_colony[0]["colo_coord"]["y"])
            if updated_colony["colo_coord"]["x"] == "-1" and updated_colony["colo_coord"]["y"] == "-1":
                updated_colony["colo_coord"]["x"] == -1
                updated_colony["colo_coord"]["y"] == -1
                updated_colony["updated"] = False
            if updated_colony["colo_coord"]["x"] != -1 and updated_colony["colo_coord"]["y"] != -1:
                updated_colony["updated"] = True
            else:
                updated_colony["colo_coord"]["x"] = -1
                updated_colony["colo_coord"]["y"] = -1
                updated_colony["updated"] = False
            self.bot.db.update_colony(updated_colony)
        elif len(db_colony) == 0:
            updated_colony = self.bot.db.push_new_colony(updated_colony)
            # if updated_colony is None:
                # await self.command_channel.send(f"> Something goes wrong while adding a colony to the player {db_player['pseudo']}.\nPlease report this bug to Softy.")
        else:
            updated_colony["_id"] = db_colony[0]["_id"]
            self.bot.db.update_colony(updated_colony)
            # await self.command_channel.send(f"> Some duplicate colonies was found for **{db_player['pseudo']}**. Updating the first one.")
            db_colony = db_colony[1:]
            for colony in db_colony:
                self.bot.db.remove_colony(colony)

    def update_colonies_from_api(self, alliance_id: int, db_player: Player_Model):
        api_players: dict = self.bot.galaxyLifeAPI.get_player_infos(db_player['id_gl'])
        api_colo_list: List[int] = list(api_players["colo_list"])
        it: int = 1
        if len(api_colo_list) != 0:
            colo_number = len(api_colo_list)
            for colo_level in api_colo_list:
                self.update_colony_from_api(it, colo_level, alliance_id, db_player)
                it += 1
        #     await self.command_channel.send(f"> **{colo_number}** 🪐 colonies were added or updated for Player named __**{db_player['pseudo']}**__.")
        # else:
        #     await self.command_channel.send(f"> No colony was added to Player named __**{db_player['pseudo']}**__.")

    def update_alliance_from_api(self, alliance: str, act_alliance: Alliance_Model):
        date: datetime.datetime = datetime.datetime.now()
        api_alliance_info: dict = self.bot.galaxyLifeAPI.get_alliance(alliance)
        act_alliance["emblem_url"] = api_alliance_info["emblem_url"]
        return_player = self.bot.db.get_one_player("pseudo", "temp_player")
        self.bot.db.update_alliance(act_alliance)
        obj: dict = {"_alliance_id": act_alliance["_id"]}
        db_players: List[Player_Model] = self.bot.db.get_players(obj)
        print(api_alliance_info["members_list"])
        for index, player in enumerate(api_alliance_info["members_list"]):
            if player["Name"].upper() == return_player['temp_pseudo'].upper():
                api_alliance_info["members_list"].insert(0, api_alliance_info["members_list"].pop(index))
                print(api_alliance_info['members_list'])
                break
        for db_player in db_players:
            player_is_in_api: bool = False
            for api_player in api_alliance_info["members_list"]:
                if api_player['Name'] == db_player["pseudo"]:
                    player_is_in_api = True
            if player_is_in_api is not True:
                db_player["_alliance_id"] = None
                self.bot.db.update_player(db_player)
        for player in api_alliance_info["members_list"]:
            player_stats: dict = self.bot.galaxyLifeAPI.get_player_stats(player["Id"])
            player_api: dict = self.bot.galaxyLifeAPI.get_player_infos(player["Id"])
            act_player: Player_Model = self.bot.db.get_one_player("pseudo", player["Name"])
            if act_player is not None:
                act_player['colonies_moved'] = player_stats['colonies_moved']
                act_player["_alliance_id"] = act_alliance["_id"]
                act_player['id_gl'] = int(player['Id'])
                if not 'online' in act_player:
                    act_player['online'] = 0
                if not 'MB_lvl' in act_player:
                    act_player['MB_lvl'] = player_api['MB_lvl']
                if not 'lvl' in act_player:
                    act_player['lvl'] = player_api["lvl"]
                if not 'MB_status' in act_player:
                    act_player['MB_status'] = 'Up'
                if not 'MB_last_attack_time' in act_player:
                    act_player['MB_last_attack_time'] = date
                    act_player['MB_refresh_time'] = date
                if not 'colonies_moved' in act_player:
                    act_player['colonies_moved'] = player_stats['colonies_moved']
                self.bot.db.update_player(act_player)
                self.update_colonies_from_api(act_alliance["_id"], act_player)
            else:
                new_player: Player_Model = {'_alliance_id': act_alliance["_id"], 'pseudo': player["Name"], "lvl": player_api["lvl"],  'id_gl': int(player["Id"]), 'MB_lvl':player_api['MB_lvl'], 'MB_status': 'Up', 'MB_last_attack_time': date, 'MB_refresh_time': date, 'bunker_full': False, 'colonies_moved': player_stats['colonies_moved'], 'online': 0}
                act_player = self.bot.db.push_new_player(new_player)
                if act_player is None:
                    continue
                    # await self.command_channel.send(f"> Something goes wrong while creating the player {player['Name']}.\nPlease report this bug to Softy.")
                else:
                    act_player = self.bot.db.get_one_player("pseudo", player["Name"])
                    act_player['id_gl'] = int(player['Id'])
                    self.bot.db.update_player(act_player)
                    self.update_colonies_from_api(act_alliance["_id"], act_player)
        return act_alliance
    
    async def update_alliance(self, alliance: str):
        act_alliance: Alliance_Model = self.bot.db.get_one_alliance("name", alliance.upper())
        if act_alliance is None:
            act_alliance = await self.add_alliance(alliance)
            if act_alliance is None:
                return None
        t: Thread = Thread(target=self.update_alliance_from_api, args=(alliance,), kwargs={'act_alliance':act_alliance}) 
        t.start()
        return act_alliance