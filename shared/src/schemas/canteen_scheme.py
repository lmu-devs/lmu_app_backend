from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import CanteenEnum
from shared.src.schemas.location_scheme import Location
from shared.src.schemas.opening_hour_scheme import OpeningHours
from shared.src.enums import CanteenTypeEnum


class CanteenBase(BaseModel):
    id: CanteenEnum
    name: str
    type: CanteenTypeEnum
    location: Location
class Canteen(CanteenBase):
    opening_hours: OpeningHours
    
class Canteens(RootModel):
    root: List[Canteen]
