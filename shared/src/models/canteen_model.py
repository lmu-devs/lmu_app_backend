from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import CanteenEnum, CanteenTypeEnum
from shared.src.models.location_model import Location
from shared.src.models.opening_hour_model import OpeningHours


class CanteenBase(BaseModel):
    id: CanteenEnum
    name: str
    type: CanteenTypeEnum
    location: Location


class Canteen(CanteenBase):
    opening_hours: OpeningHours
    url_id: int | None = None


class Canteens(RootModel):
    root: List[Canteen]
