from typing import List
from pydantic import BaseModel, RootModel

from shared.src.tables.roomfinder.building_table import BuildingTable
from api.src.v1.roomfinder.models.building_part_model import BuildingParts
from shared.src.models.location_model import Location

class Building(BaseModel):
    id: str
    title: str
    location: Location
    building_parts: BuildingParts

    @classmethod
    def from_table(cls, data: BuildingTable) -> "Building":
        return Building(
            id=data.id,
            title=data.display_name,
            location=Location.from_table(data.location),
            building_parts=BuildingParts.from_table(data.building_parts),
        )

class Buildings(RootModel):
    root: List[Building]

    @classmethod
    def from_table(cls, data: List[BuildingTable]) -> "Buildings":
        return Buildings(root=[Building.from_table(building) for building in data])
