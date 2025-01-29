from typing import Dict, List

from pydantic import BaseModel


class Building(BaseModel):
    code: str
    streetCode: str
    displayName: str
    lat: float
    lng: float

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Building":
        return cls(**data)
    
    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, str]]) -> List["Building"]:
        return [cls.from_dict(item) for item in json_list]
