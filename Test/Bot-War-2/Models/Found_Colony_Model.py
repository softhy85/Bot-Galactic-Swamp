from typing import TypedDict
from bson.objectid import ObjectId
from Models.Coord import Coord
import datetime


class Colony_Model(TypedDict):
    _id: ObjectId
    id_gl: str
    colo_sys_name: str
    colo_lvl: int
    colo_coord: Coord

