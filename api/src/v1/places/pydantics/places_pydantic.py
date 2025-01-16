from typing import List

from shared.src.tables import CanteenLocationTable, CinemaLocationTable
from api.src.v1.places.schemas.places_scheme import Place, PlaceEnum
from api.src.v1.core.pydantics.location_pydantic import location_to_pydantic


async def places_to_pydantic(places: List[CanteenLocationTable | CinemaLocationTable]) -> List[Place]:
    places_pydantic = []
    for place in places:
        if isinstance(place, CanteenLocationTable):
            place_type = PlaceEnum.CANTEEN
            id = place.canteen_id
        elif isinstance(place, CinemaLocationTable):
            place_type = PlaceEnum.CINEMA
            id = place.cinema_id
        else:
            raise ValueError(f"Invalid place type: {type(place)}")
        
        places_pydantic.append(
            Place(
                id=id,
                location=location_to_pydantic(place),
                type=place_type
            )
        )
    return places_pydantic