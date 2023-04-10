import datetime
import os
from pymongo import MongoClient
from pymongo.cursor import Cursor
from Models.Alliance_Model import Alliance_Model
from Models.Player_Model import Player_Model
from Models.Colony_Model import Colony_Model
from Models.InfoMessage_Model import InfoMessage_Model
from Models.War_Model import War_Model
from bson.objectid import ObjectId
from dotenv import load_dotenv

# TODO 1 - voir comment faire pour les nombres de colonies en auto
# TODO 2 - (si il est fait directement lors du add, ou une fonction précédente permetant de remplir les infos de la colo)

class DataBase:
    mongo_client: MongoClient = None
    db_name: str = ""

    def __init__(self) -> None:
        self.mongo_client = MongoClient(os.getenv("MONGO_CO"))
        self.db_name = os.getenv("MONGO_DB_NAME")
        self.db = self.mongo_client[self.db_name]

    def push_new_info_message(self, info_message: InfoMessage_Model) -> ObjectId | None:
        return self.db.infoMessages.insert_one(info_message).inserted_id

    def update_info_message(self, info_message: InfoMessage_Model) -> None:
        return_info_message: Alliance_Model = self.db.infoMessages.find_one({"_id": info_message["_id"]})
        if return_info_message is not None:
            self.db.infoMessages.update_one({"_id": info_message["_id"]}, {'$set': info_message})

    def remove_info_message(self, info_message: InfoMessage_Model) -> None:
        self.db.infoMessages.delete_one({"_id": info_message["_id"]})

    def get_one_info_message(self, name: str, value: any) -> InfoMessage_Model:
        return self.db.infoMessages.find_one({name: value})

    def get_info_messages(self, obj: dict) -> Cursor[InfoMessage_Model]:
        return self.db.infoMessages.find(obj)

    def push_new_alliance(self, alliance: Alliance_Model) -> ObjectId | None:
        existing_alliance: Alliance_Model = self.db.alliances.find_one({"name": alliance["name"]})
        if existing_alliance is None:
            return self.db.alliances.insert_one(alliance).inserted_id
        return None

    def update_alliance(self, alliance: Alliance_Model) -> None:
        return_alliance: Alliance_Model = self.db.alliances.find_one({"_id": alliance["_id"]})
        if alliance["_id"] == return_alliance["_id"]:
            self.db.alliances.update_one({"_id": alliance["_id"]}, {'$set': alliance})

    def remove_alliance(self, alliance: Alliance_Model) -> None:
        self.db.alliances.delete_one({"_id": alliance["_id"]})
        self.db.players.delete_many({"_alliance_id": alliance["_id"]})
        self.db.colonies.delete_many({"_alliance_id": alliance["_id"]})

    def get_one_alliance(self, name: str, value: any) -> Alliance_Model:
        return self.db.alliances.find_one({name: value})

    def get_alliances(self, obj: dict) -> Cursor[Alliance_Model]:
        return self.db.alliances.find(obj)

    def get_all_alliances(self) -> Cursor[Alliance_Model]:
        return self.db.alliances.find()

    def push_new_player(self, player: Player_Model) -> ObjectId | None:
        existing_player: Player_Model = self.db.players.find_one({"pseudo": player["pseudo"]})
        existing_alliance: Alliance_Model = self.db.alliances.find_one({"_id": player["_alliance_id"]})
        if existing_player is None and existing_alliance is not None:
            return self.db.players.insert_one(player).inserted_id
        return None

    def update_player(self, player: Player_Model) -> None:
        return_player: Player_Model = self.db.players.find_one({"_id": player["_id"]})
        if player["_id"] == return_player["_id"]:
            self.db.players.update_one({"_id": player["_id"]}, {'$set': player})

    def remove_player(self, player: Player_Model) -> None:
        self.db.players.delete_one({"_id": player["_id"]})
        self.db.colonies.delete_many({"_player_id": player["_id"]})

    def get_one_player(self, name: str, value: any) -> Player_Model:
        return self.db.players.find_one({name: value})

    def get_players(self, obj: dict) -> Cursor[Player_Model]:
        return self.db.players.find(obj)

    def get_all_players(self) -> Cursor[Player_Model]:
        return self.db.players.find()

    def push_new_colony(self, colony: Colony_Model) -> ObjectId | None:
        existing_colony: Colony_Model = self.db.player.find_one({"_player_id": colony["_player_id"], "number": colony["number"]})
        existing_player: Player_Model = self.db.players.find_one({"_id": colony["_player_id"]})
        existing_alliance: Alliance_Model = self.db.alliances.find_one({"_id": colony["_alliance_id"]})
        if existing_colony is None and existing_player is not None and existing_alliance is not None:
            return self.db.colonies.insert_one(colony).inserted_id
        return None

    def update_colony(self, colony: Colony_Model) -> None:
        return_colony: Colony_Model = self.db.colonies.find_one({"_id": colony["_id"]})
        if colony["_id"] == return_colony["_id"]:
            self.db.colonies.update_one({"_id": colony["_id"]}, {'$set': colony})

    def remove_colony(self, colony: Colony_Model) -> None:
        self.db.colonies.delete_one({"_id": colony["_id"]})

    def get_one_colony(self, name: str, value: any) -> Colony_Model:
        return self.db.colonies.find_one({name: value})

    def get_colonies(self, obj: dict) -> Cursor[Colony_Model]:
        return self.db.colonies.find(obj)

    def get_all_colonies(self) -> Cursor[Colony_Model]:
        return self.db.colonies.find()
    
    def get_all_updated_colonies(self) -> Cursor[Colony_Model]:
        return self.db.colonies.find({"updated": True})
    # def get_scouted_colonies(self, obj: dict) -> Cursor[Colony_Model]:
    #     return self.db.colonies.find(obj)
        
    def push_new_war(self, war: War_Model) -> ObjectId | None:
        actual_war: War_Model = self.db.wars.find_one({"status": "InProgress"})
        if actual_war is None:
            return self.db.wars.insert_one(war).inserted_id
        return None

    def update_war(self, war: War_Model) -> None:
        return_war: War_Model = self.db.wars.find_one({"_id": war["_id"]})
        if return_war is not None:
            self.db.wars.update_one({"_id": war["_id"]}, {'$set': war})

    def remove_war(self, war: War_Model) -> None:
        self.db.wars.delete_one({"_id": war["_id"]})

    def get_one_war(self, name: str, value: any) -> War_Model:
        return self.db.wars.find_one({name: value})

    def get_wars(self, obj: dict) -> Cursor[War_Model]:
        return self.db.wars.find(obj)

    def close(self) -> None:
        self.mongo_client.close()


if __name__ == '__main__':
    load_dotenv()
    db = DataBase()
    date = datetime.datetime.now()
    alliance: Alliance_Model = {"name": "Test", "alliance_lvl": 1}
    alliance["_id"] = db.push_new_alliance(alliance)
    war: War_Model = {'_alliance_id': alliance["_id"], 'alliance_name': alliance["name"], 'id_thread': 0, 'status': "InProgress", 'point': 0, 'enemy_point': 0}
    war["_id"] = db.push_new_war(war)
    player: Player_Model = {"_alliance_id": alliance["_id"], "pseudo": "Softy", "lvl": 1, 'MB_sys_name': "AAAA", 'MB_lvl': 1, 'MB_status': "Up", 'MB_last_attack_time': date, 'SB_refresh_time': date}
    player["_id"] = db.push_new_player(player)
    colony: Colony_Model = {'_alliance_id': alliance["_id"], "_player_id": player["_id"], 'number': 1, 'colo_sys_name': "BBBBB", 'colo_lvl': 1, 'colo_coord': {"x": 1, "y": 1}, 'colo_status': "Up", 'colo_last_attack_time': date, 'colo_refresh_time': date}
    colony["_id"] = db.push_new_colony(colony)
