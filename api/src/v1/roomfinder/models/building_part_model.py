from typing import Dict, List

from pydantic import BaseModel
from shared.src.tables.roomfinder.building_part_table import BuildingPartTable

from data_fetcher.src.roomfinder.models.floor_model import Floor

class BuildingPart(BaseModel):
    code: str
    address: str
    floors: List[Floor]
    
    @classmethod
    def from_db(cls, data: BuildingPartTable) -> "BuildingPart":
        return cls(**data)
