from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables.roomfinder.room_table import RoomTable


class Room(BaseModel):
    id: str
    name: str

    @classmethod
    def from_table(cls, data: RoomTable) -> "Room":
        return Room(
            id=data.id,
            name=data.name,
        )


class Rooms(RootModel):
    root: List[Room]

    @classmethod
    def from_table(cls, data: List[RoomTable]) -> "Rooms":
        return Rooms(root=[Room.from_table(room) for room in data])
