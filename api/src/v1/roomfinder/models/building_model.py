from typing import List
from pydantic import BaseModel

from shared.src.tables.roomfinder.building_table import BuildingTable
from data_fetcher.src.roomfinder.models.street_model import Street
from data_fetcher.src.roomfinder.models.building_part_model import BuildingPart

class Building(BaseModel):
    code: str
    building_parts: List[BuildingPart]
    display_name: str
    lat: float
    lng: float

    @classmethod
    def from_db(cls, data: BuildingTable) -> "Building":
        return cls(**data)
