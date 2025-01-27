from typing import Dict, List

from pydantic import BaseModel


class BuildingPart(BaseModel):
    code: str
    buildingCode: str
    address: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "BuildingPart":
        return cls(**data)

    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, str]]) -> List["BuildingPart"]:
        return [cls.from_dict(item) for item in json_list]
