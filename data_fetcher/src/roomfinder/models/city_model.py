from typing import Dict, List

from pydantic import BaseModel


class City(BaseModel):
    code: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "City":
        return cls(**data)

    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, str]]) -> List["City"]:
        return [cls.from_dict(item) for item in json_list]
