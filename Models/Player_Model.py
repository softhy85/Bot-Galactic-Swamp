from typing import TypedDict
from bson.objectid import ObjectId
from Models.Coord import Coord
from enum import Enum
import datetime


class Player_Status(Enum):
    Private = -1
    Connected = 0
    Disconnected = 1


class Player_Model(TypedDict):
    _id: ObjectId
    _alliance_id: ObjectId
    id_gl: str
    pseudo: str
    lvl: int
    online: int
    MB_sys_name: str
    MB_lvl: int
    MB_status: str
    MB_last_attack_time: datetime
    MB_refresh_time: datetime
    
    
