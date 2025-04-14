from typing import Dict, List

from pydantic import BaseModel


class Floor(BaseModel):
    code: str
    buildingPartCode: str
    level: str
    name: str
    mapUri: str
    mapSizeX: int
    mapSizeY: int

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Floor":
        return cls(**data)

    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, str]]) -> List["Floor"]:
        return [cls.from_dict(item) for item in json_list]
