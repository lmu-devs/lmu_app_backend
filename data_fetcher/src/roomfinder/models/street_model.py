from typing import Dict, List

from pydantic import BaseModel


class Street(BaseModel):
    code: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Street":
        return cls(**data)

    @classmethod
    def from_json_list(cls, json_list: List[Dict[str, str]]) -> List["Street"]:
        return [cls.from_dict(item) for item in json_list]
