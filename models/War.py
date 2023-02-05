from typing import TypedDict
from bson.objectid import ObjectId


class War(TypedDict):
    _id: ObjectId
    _id_faction: ObjectId
    faction_name: str
    id_thread: str
    enemy_point: int
    point: int
    status: str