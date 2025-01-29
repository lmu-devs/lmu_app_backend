from enum import Enum

from pydantic import BaseModel

from shared.src.models import Location


class PlaceEnum(str, Enum):
    CANTEEN = "canteen"
    BISTRO = "bistro"
    COFFEE = "coffee"
    LOUNGE = "lounge"
    BIBLIOTHEQUE = "bibliotheque"
    BUILDING = "building"
    CINEMA = "cinema"

class Place(BaseModel):
    id: str
    location: Location
    type: PlaceEnum