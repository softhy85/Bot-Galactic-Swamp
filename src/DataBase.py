import os
from pymongo import MongoClient
from models.Alliance import Alliance
from models.Player import Player
from models.Colony import Colony
from models.InfoMessage import InfoMessage
from bson.objectid import ObjectId
from dotenv import load_dotenv

# TODO 1 - voir comment faire pour les nombres de colonies en auto
# TODO 2 - (si il est fait directement lors du add, ou une fonction précédente permetant de remplir les infos de la colo)

class DataBase:
    mongo_client: MongoClient = None
    db_name: str = ""

    def __init__(self):
        self.mongo_client = MongoClient(os.getenv("MONGO_CO"))
        self.db_name = "Galactic-Swamp"
        self.db = self.mongo_client[self.db_name]

    def push_new_info_message(self, info_message: InfoMessage):
        self.db.infoMessages.insert_one(info_message)

    def update_info_message(self, info_message: InfoMessage):
        return_info_message: Alliance = self.db.infoMessages.find_one({"_id": info_message["_id"]})
        if alliance["_id"] == return_info_message["_id"]:
            self.db.infoMessages.update({"_id": info_message["_id"]}, {'$set': {info_message}})

    def remove_info_message(self, info_message: InfoMessage):
        self.db.infoMessages.delete({"_id": info_message["_id"]})

    def get_one_info_message(self, name: str, value: str):
        return self.db.infoMessages.find_one({name: value})

    def get_info_messages(self, name: str, value: str):
        return self.db.infoMessages.find({name: value})

    def push_new_alliance(self, alliance: Alliance):
        existing_alliance: Player = self.db.alliances.find_one({"_id": alliance["_id"]})
        if existing_alliance is None:
            self.db.alliances.insert_one(alliance)

    def update_alliance(self, alliance: Alliance):
        return_alliance: Alliance = self.db.alliances.find_one({"_id": alliance["_id"]})
        if alliance["_id"] == return_alliance["_id"]:
            self.db.alliances.update({"_id": alliance["_id"]}, {'$set': {alliance}})

    def remove_alliance(self, alliance: Alliance):
        self.db.alliances.delete_one({"_id": alliance["_id"]})
        self.db.players.delete({"_alliance_id": alliance["_id"]})
        self.db.colonies.delete({"_alliance_id": alliance["_id"]})

    def get_one_alliance(self, name: str, value: str):
        return self.db.alliances.find_one({name: value})

    def get_alliances(self, name: str, value: str):
        return self.db.alliances.find({name: value})

    def push_new_player(self, player: Player):
        existing_player: Player = self.db.players.find_one({"pseudo": player["pseudo"]})
        existing_alliance: Alliance = self.db.alliances.find_one({"_id": player["_alliance_id"]})
        if existing_player is None and existing_alliance is not None:
            self.db.players.insert_one(player)

    def update_player(self, player: Player):
        return_player: Player = self.db.players.find_one({"_id": player["_id"]})
        if player["_id"] == return_player["_id"]:
            self.db.players.update({"_id": player["_id"]}, {'$set': {player}})

    def remove_player(self, player: Player):
        self.db.players.delete({"_id": player["_id"]})
        self.db.colonies.delete({"_player_id": player["_id"]})

    def get_one_player(self, name: str, value: str):
        return self.db.players.find_one({name: value})

    def get_players(self, name: str, value: str):
        return self.db.players.find({name: value})

    def push_new_colony(self, colony: Colony):
        existing_player: Player = self.db.players.find_one({"_id": colony["_player_id"]})
        existing_alliance: Alliance = self.db.alliances.find_one({"_id": colony["_alliance_id"]})
        if existing_player is not None and existing_alliance is not None:
            self.db.colonies.insert_one(colony)

    def update_colony(self, colony: Colony):
        return_colony: Colony = self.db.colonies.find_one({"_id": colony["_id"]})
        if colony["_id"] == return_colony["_id"]:
            self.db.colonies.update({"_id": colony["_id"]}, {'$set': {colony}})

    def remove_colony(self, colony: Colony):
        self.db.colonies.delete({"_id": colony["_id"]})

    def get_one_colony(self, name: str, value: str):
        return self.db.colonies.find_one({name: value})

    def get_colonies(self, name: str, value: str):
        return self.db.colonies.find({name: value})

    def players_from_alliance(self, name: str, value: str):
        id_alliance: ObjectId
        if name == "_id":
            id_alliance = ObjectId(value)
        else:
            existing_alliance: Alliance = self.db.alliances.find_one({name: value})
            if existing_alliance is None:
                return []
            id_alliance = existing_alliance["_id"]
        return self.db.alliances.find({["_alliance_id"]: id_alliance})

    def colonies_from_player(self, name: str, value: str):
        id_player: ObjectId
        if name == "_id":
            id_player = ObjectId(value)
        else:
            existing_player: Alliance = self.db.players.find_one({name: value})
            if existing_player is None:
                return []
            id_player = existing_player["_id"]
        return self.db.alliances.find({["_alliance_id"]: id_player})


    def close(self):
        self.mongo_client.close()


if __name__ == '__main__':
    load_dotenv()
    db = DataBase()
    alliance: Alliance = {"name": "Test", "alliance_lvl": 1, "status": "Oui"}
    db.push_new_alliance(alliance)
