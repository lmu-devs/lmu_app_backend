from typing import Dict, List

from pydantic import BaseModel


class Room(BaseModel):
    code: str
    name: str
    floorCode: str
    posX: int
    posY: int

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Room":
        return cls(**data)

    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, str]]) -> List["Room"]:
        return [cls.from_dict(item) for item in json_list]
