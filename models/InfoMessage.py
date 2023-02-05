from typing import TypedDict
from bson.objectid import ObjectId


class InfoMessage(TypedDict):
    _id: ObjectId
    _id_linked: ObjectId
    id_embed: str
    type_embed: str
