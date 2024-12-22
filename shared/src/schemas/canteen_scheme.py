from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import CanteenEnum
from shared.src.schemas.location_scheme import Location
from shared.src.schemas.opening_hour_scheme import OpeningHours
from shared.src.schemas.rating_scheme import Rating
from shared.src.schemas.image_scheme import Image
from shared.src.tables import CanteenTypeEnum


class Canteen(BaseModel):
    id: CanteenEnum
    name: str
    type: CanteenTypeEnum
    location: Location
    opening_hours: OpeningHours
    
class Canteens(RootModel):
    root: List[Canteen]
