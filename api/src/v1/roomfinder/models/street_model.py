from typing import List
from pydantic import BaseModel, RootModel

from shared.src.tables.roomfinder.street_table import StreetTable

from api.src.v1.roomfinder.models.building_model import Buildings


class Street(BaseModel):
    id: str
    name: str
    buildings: Buildings

    @classmethod
    def from_table(cls, data: StreetTable) -> "Street":
        return Street(
            id=data.id,
            name=data.name,
            buildings=Buildings.from_table(data.buildings),
        )


class Streets(RootModel):
    root: List[Street]

    @classmethod
    def from_table(cls, data: List[StreetTable]) -> "Streets":
        return Streets(root=[Street.from_table(street) for street in data])
