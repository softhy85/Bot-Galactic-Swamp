from typing import TypedDict
from bson.objectid import ObjectId
from Models.Coord import Coord
import datetime


class Next_War_Model(TypedDict):
    _id: ObjectId
    name: str
    start_time: int
    players_online_list: str
    positive_votes: int
    negative_votes: int
    vote_done: bool