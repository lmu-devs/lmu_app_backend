from typing import Dict, List

from pydantic import BaseModel
from shared.src.tables.roomfinder.room_table import RoomTable

class Room(BaseModel):
    code: str
    name: str
    posX: int
    posY: int

    @classmethod
    def from_db(cls, data: RoomTable) -> "Room":
        return cls(**data)
