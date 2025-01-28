from typing import List
from pydantic import BaseModel

from shared.src.tables.roomfinder.floor_table import FloorTable
from data_fetcher.src.roomfinder.models.room_model import Room

class Floor(BaseModel):
    code: str
    level: str
    name: str
    map_uri: str
    map_size_x: int
    map_size_y: int
    rooms: List[Room]

    @classmethod
    def from_db(cls, data: FloorTable) -> "Floor":
        return cls(**data)
