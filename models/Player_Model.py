from typing import TypedDict
from bson.objectid import ObjectId
from models.Coord import Coord
import datetime

class Player_Model(TypedDict):
    _id: ObjectId
    _alliance_id: ObjectId
    _steam_id: ObjectId
    pseudo: str
    lvl: int
    status: str
    MB_sys_name: str
    MB_lvl: int
    MB_status: str
    MB_last_attack_time: datetime
    MB_refresh_time: datetime
    colo_total_number: int
    
