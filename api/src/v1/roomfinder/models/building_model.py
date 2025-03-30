from typing import List
from pydantic import BaseModel, RootModel

from api.src.v1.roomfinder.models.floor_model import Floors
from shared.src.tables.roomfinder.building_table import BuildingTable
from shared.src.models.location_model import Location

class Building(BaseModel):
    building_id: str
    building_part_id: str
    title: str
    aliases: list[str]
    location: Location
    floors: Floors

    @classmethod
    def from_table(cls, building: BuildingTable) -> "Building":
        return Building(
            building_id=building.building_id,
            building_part_id=building.building_part_id,
            title=building.title,
            aliases=building.aliases,
            location=Location.from_table(building.location),
            floors=Floors.from_table(building.floors),
        )

class Buildings(RootModel):
    root: List[Building]

    @classmethod
    def from_table(cls, data: List[BuildingTable]) -> "Buildings":
        return Buildings(root=[Building.from_table(building) for building in data])
