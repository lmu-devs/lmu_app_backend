from enum import Enum
from typing import List

from pydantic import BaseModel

from shared.src.models import Location
from shared.src.tables import (
    BuildingLocationTable,
    CanteenLocationTable,
    CinemaLocationTable,
)


class PlaceEnum(str, Enum):
    CANTEEN = "CANTEEN"
    BISTRO = "BISTRO"
    COFFEE = "COFFEE"
    LOUNGE = "LOUNGE"
    BIBLIOTHEQUE = "BIBLIOTHEQUE"
    BUILDING = "BUILDING"
    CINEMA = "CINEMA"


class Place(BaseModel):
    id: str
    location: Location
    type: PlaceEnum

    @classmethod
    def places_to_pydantic(
        cls,
        places: List[BuildingLocationTable | CanteenLocationTable | CinemaLocationTable],
    ) -> List["Place"]:
        places_pydantic = []
        for place in places:
            if isinstance(place, CanteenLocationTable):
                place_type = PlaceEnum.CANTEEN
                id = place.canteen_id
            elif isinstance(place, CinemaLocationTable):
                place_type = PlaceEnum.CINEMA
                id = place.cinema_id
            elif isinstance(place, BuildingLocationTable):
                place_type = PlaceEnum.BUILDING
                id = place.building_id
            else:
                raise ValueError(f"Invalid place type: {type(place)}")

            places_pydantic.append(Place(id=id, location=Location.from_table(place.location), type=place_type))
        return places_pydantic
