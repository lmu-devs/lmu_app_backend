from typing import List
from pydantic import BaseModel, RootModel

from shared.src.tables.roomfinder.room_table import RoomTable

class Room(BaseModel):
    id: str
    name: str
    pos_x: int
    pos_y: int

    @classmethod
    def from_table(cls, data: RoomTable) -> "Room":
        return Room(
            id=data.id,
            name=data.name,
            pos_x=data.pos_x,
            pos_y=data.pos_y,
        )


class Rooms(RootModel):
    root: List[Room]

    @classmethod
    def from_table(cls, data: List[RoomTable]) -> "Rooms":
        return Rooms(root=[Room.from_table(room) for room in data])
