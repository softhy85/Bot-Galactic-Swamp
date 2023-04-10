from typing import TypedDict
from enum import Enum
from bson.objectid import ObjectId
import datetime

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
    ally_initial_score: int
    initial_enemy_score: int
    status: str
    start_time : datetime
    refresh_duration: float