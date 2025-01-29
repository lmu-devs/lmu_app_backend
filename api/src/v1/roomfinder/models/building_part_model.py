from typing import List

from pydantic import BaseModel, RootModel
from shared.src.tables.roomfinder.building_part_table import BuildingPartTable

from api.src.v1.roomfinder.models.floor_model import Floors

class BuildingPart(BaseModel):
    id: str
    address: str
    floors: Floors
    
    @classmethod
    def from_table(cls, data: BuildingPartTable) -> "BuildingPart":
        return BuildingPart(
            id=data.id,
            address=data.address,
            floors=Floors.from_table(data.floors),
        )

class BuildingParts(RootModel):
    root: List[BuildingPart]

    @classmethod
    def from_table(cls, data: List[BuildingPartTable]) -> "BuildingParts":
        return BuildingParts(root=[BuildingPart.from_table(building_part) for building_part in data])
