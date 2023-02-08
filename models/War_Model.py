from typing import TypedDict
from enum import Enum
from bson.objectid import ObjectId

class Status(Enum):
    InProgress = 1
    Win = 2
    Lost = 3
    Ended = 4

class War_Model(TypedDict):
    _id: ObjectId
    _alliance_id: ObjectId
    alliance_name: str
    id_thread: int
    point: int
    enemy_point: int
    status: str