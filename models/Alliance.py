from typing import TypedDict
from bson.objectid import ObjectId


class Alliance(TypedDict):
    _id: ObjectId
    name: str
    faction_lvl: int
