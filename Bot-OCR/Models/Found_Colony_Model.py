from typing import TypedDict
from bson.objectid import ObjectId
from Models.Coord import Coord
import datetime


class Found_Colony_Model(TypedDict):
    _id: ObjectId
    gl_id: str
    colo_sys_name: str
    colo_lvl: int
    X: int
    Y: int

