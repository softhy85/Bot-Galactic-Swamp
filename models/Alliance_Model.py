from typing import TypedDict
from bson.objectid import ObjectId


class Alliance_Model(TypedDict):
    _id: ObjectId
    name: str
    alliance_lvl: int
