from typing import TypedDict
from bson.objectid import ObjectId
from models.Coord import Coord
import datetime


class Colony_Model(TypedDict):
    _id: ObjectId
    _player_id: ObjectId
    _alliance_id: ObjectId
    number: int
    colo_sys_name: str
    colo_lvl: int
    colo_coord: Coord
    colo_status: str
    colo_last_attack_time: datetime
    colo_refresh_time: datetime
    updated: bool
