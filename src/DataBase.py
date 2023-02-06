import os
from pymongo import MongoClient
from models.Alliance_Model import Alliance_Model
from models.Player_Model import Player_Model
from models.Colony_Model import Colony_Model
from models.InfoMessage_Model import InfoMessage_Model
from models.War_Model import War_Model
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

    def push_new_info_message(self, info_message: InfoMessage_Model):
        return self.db.infoMessages.insert_one(info_message)

    def update_info_message(self, info_message: InfoMessage_Model):
        return_info_message: Alliance_Model = self.db.infoMessages.find_one({"_id": info_message["_id"]})
        if return_info_message is not None:
            self.db.infoMessages.update_one({"_id": info_message["_id"]}, {'$set': info_message})

    def remove_info_message(self, info_message: InfoMessage_Model):
        self.db.infoMessages.delete_one({"_id": info_message["_id"]})

    def get_one_info_message(self, name: str, value: str):
        return self.db.infoMessages.find_one({name: value})

    def get_info_messages(self, name: str, value: str):
        return self.db.infoMessages.find({name: value})

    def push_new_alliance(self, alliance: Alliance_Model):
        existing_alliance: Alliance_Model = self.db.alliances.find_one({"name": alliance["name"]})
        if existing_alliance is None:
            return self.db.alliances.insert_one(alliance)
        return None

    def update_alliance(self, alliance: Alliance_Model):
        return_alliance: Alliance_Model = self.db.alliances.find_one({"_id": alliance["_id"]})
        if alliance["_id"] == return_alliance["_id"]:
            self.db.alliances.update_one({"_id": alliance["_id"]}, {'$set': alliance})

    def remove_alliance(self, alliance: Alliance_Model):
        self.db.alliances.delete_one({"_id": alliance["_id"]})
        self.db.players.delete_many({"_alliance_id": alliance["_id"]})
        self.db.colonies.delete_many({"_alliance_id": alliance["_id"]})

    def get_one_alliance(self, name: str, value: str):
        return self.db.alliances.find_one({name: value})

    def get_alliances(self, name: str, value: str):
        return self.db.alliances.find({name: value})
    def get_all_alliances(self):
        return self.db.alliances.find()

    def push_new_player(self, player: Player_Model):
        existing_player: Player_Model = self.db.players.find_one({"pseudo": player["pseudo"]})
        existing_alliance: Alliance_Model = self.db.alliances.find_one({"_id": player["_alliance_id"]})
        if existing_player is None and existing_alliance is not None:
            return self.db.players.insert_one(player)
        return None

    def update_player(self, player: Player_Model):
        return_player: Player_Model = self.db.players.find_one({"_id": player["_id"]})
        if player["_id"] == return_player["_id"]:
            self.db.players.update_one({"_id": player["_id"]}, {'$set': player})

    def remove_player(self, player: Player_Model):
        self.db.players.delete({"_id": player["_id"]})
        self.db.colonies.delete_many({"_player_id": player["_id"]})

    def get_one_player(self, name: str, value: str):
        return self.db.players.find_one({name: value})

    def get_players(self, name: str, value: str):
        return self.db.players.find({name: value})

    def push_new_colony(self, colony: Colony_Model):
        existing_colony: Colony_Model = self.db.player.find_one({"_player_id": colony["_player_id"], "number": colony["number"]})
        existing_player: Player_Model = self.db.players.find_one({"_id": colony["_player_id"]})
        existing_alliance: Alliance_Model = self.db.alliances.find_one({"_id": colony["_alliance_id"]})
        if existing_colony is None and existing_player is not None and existing_alliance is not None:
            return self.db.colonies.insert_one(colony)
        return None

    def update_colony(self, colony: Colony_Model):
        return_colony: Colony_Model = self.db.colonies.find_one({"_id": colony["_id"]})
        if colony["_id"] == return_colony["_id"]:
            self.db.colonies.update_one({"_id": colony["_id"]}, {'$set': colony})

    def remove_colony(self, colony: Colony_Model):
        self.db.colonies.delete_one({"_id": colony["_id"]})

    def get_one_colony(self, name: str, value: str):
        return self.db.colonies.find_one({name: value})

    def get_colonies(self, name: str, value: str):
        return self.db.colonies.find({name: value})

    def players_from_alliance(self, name: str, value: str):
        id_alliance: ObjectId
        if name == "_id":
            id_alliance = ObjectId(value)
        else:
            existing_alliance: Alliance_Model = self.db.alliances.find_one({name: value})
            if existing_alliance is None:
                return []
            id_alliance = existing_alliance["_id"]
        return self.db.alliances.find({["_alliance_id"]: id_alliance})

    def colonies_from_player(self, name: str, value: str):
        id_player: ObjectId
        if name == "_id":
            id_player = ObjectId(value)
        else:
            existing_player: Alliance_Model = self.db.players.find_one({name: value})
            if existing_player is None:
                return []
            id_player = existing_player["_id"]
        return self.db.alliances.find({["_alliance_id"]: id_player})

    def push_new_war(self, war: War_Model):
        actual_war: War_Model = self.db.wars.find_one({"status": "InProgress"})
        if actual_war is None:
            return self.db.wars.insert_one(war)
        return None

    def update_war(self, war: War_Model):
        return_war: War_Model = self.db.wars.find_one({"_id": war["_id"]})
        if return_war is not None:
            self.db.wars.update_one({"_id": war["_id"]}, {'$set': war})

    def remove_war(self, war: War_Model):
        self.db.wars.delete_one({"_id": war["_id"]})

    def get_one_war(self, name: str, value: str):
        return self.db.wars.find_one({name: value})

    def get_wars(self, name: str, value: str):
        return self.db.wars.find({name: value})

    def close(self):
        self.mongo_client.close()


if __name__ == '__main__':
    load_dotenv()
    db = DataBase()
    alliance: Alliance_Model = {"name": "Test", "alliance_lvl": 1, "status": "Oui"}
    db.push_new_alliance(alliance)
