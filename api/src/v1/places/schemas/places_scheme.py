from enum import Enum
from pydantic import BaseModel
from shared.src.schemas.location_scheme import Location

class PlaceEnum(str, Enum):
    CANTEEN = "canteen"
    BISTRO = "bistro"
    COFFEE = "coffee"
    LOUNGE = "lounge"
    BIBLIOTHEQUE = "bibliotheque"
    BUILDING = "building"
    CINEMA = "cinema"

class Places(BaseModel):
    location: Location
    name: str
    type: PlaceEnum
    description: str