from typing import List
from pydantic import BaseModel, RootModel

from shared.src.tables.roomfinder.city_table import CityTable
from api.src.v1.roomfinder.models.street_model import Streets

class City(BaseModel):
    id: str
    name: str
    streets: Streets

    @classmethod
    def from_table(cls, data: CityTable) -> 'City':
        return cls(
            id=data.id,
            name=data.name,
            streets=Streets.from_table(data.streets),
        )


class Cities(RootModel):
    root: List[City]

    @classmethod
    def from_table(cls, data: List[CityTable]) -> "Cities":
        return cls(root=[City.from_table(city) for city in data])
