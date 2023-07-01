from typing import TypedDict
from bson.objectid import ObjectId


class InfoMessage_Model(TypedDict):
    _id: ObjectId
    _id_linked: ObjectId
    id_message: int
    type_embed: str
