from typing import List
from pydantic import BaseModel

from shared.src.tables.roomfinder.city_table import CityTable
from data_fetcher.src.roomfinder.models.street_model import Street

class City(BaseModel):
    code: str
    name: str
    streets: List[Street]

    @classmethod
    def from_db(cls, data: CityTable) -> "City":
        return cls(**data)
