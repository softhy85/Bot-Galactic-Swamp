from typing import TypedDict
from bson.objectid import ObjectId
from Models.Coord import Coord
import datetime


class War_Log_Model(TypedDict):
    _id: ObjectId
    name: str
    ennemy_score: list
    ally_score: list
    timestamp: int