from typing import TypedDict
from bson.objectid import ObjectId
from Models.Coord import Coord
import datetime


class Colonies_List_Model(TypedDict):
    _id: ObjectId
    name: str
    list: list
