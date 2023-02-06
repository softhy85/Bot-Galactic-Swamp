from typing import TypedDict
from bson.objectid import ObjectId
from models.Coord import Coord
import datetime

class Player_Model(TypedDict):
    _id: ObjectId
    _alliance_id: ObjectId
    pseudo: str
    lvl: int
    SB_sys_name: str
    SB_lvl: int
    SB_status: str
    SB_last_attack_time: datetime
    SB_refresh_time: datetime
