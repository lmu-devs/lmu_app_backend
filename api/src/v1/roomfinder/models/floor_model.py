from typing import List
from pydantic import BaseModel, RootModel

from shared.src.tables.roomfinder.floor_table import FloorTable
from api.src.v1.roomfinder.models.room_model import Rooms

class Floor(BaseModel):
    id: str
    name: str
    map_uri: str
    map_size_x: int
    map_size_y: int
    rooms: Rooms

    @classmethod
    def from_table(cls, data: FloorTable) -> "Floor":
        return Floor(
            id=data.id,
            name=data.name,
            map_uri=data.map_uri,
            map_size_x=data.map_size_x,
            map_size_y=data.map_size_y,
            rooms=Rooms.from_table(data.rooms),
        )

class Floors(RootModel):
    root: List[Floor]

    @classmethod
    def from_table(cls, data: List[FloorTable]) -> "Floors":
        return Floors(root=[Floor.from_table(floor) for floor in data])
