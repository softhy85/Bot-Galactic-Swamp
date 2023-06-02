import datetime
from enum import Enum
from typing import TypedDict

from bson.objectid import ObjectId

from Models.Coord import Coord


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
    last_attack_time: datetime
    MB_sys_name: str
    MB_lvl: int
    MB_status: str
    MB_last_attack_time: datetime
    MB_refresh_time: datetime
    colonies_moved: int
    colonies_moved_bool: bool
    total_war_points: int
    war_points_delta: int
    bunker_troops: int
    
    
