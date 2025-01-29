from typing import List

from shared.src.tables import CanteenLocationTable, CinemaLocationTable, BuildingLocationTable
from api.src.v1.places.models.places_model import Place, PlaceEnum
from shared.src.models.location_model import Location

async def places_to_pydantic(places: List[any]) -> List[Place]:
    places_pydantic = []
    for place in places:
        if isinstance(place, CanteenLocationTable):
            place_type = PlaceEnum.CANTEEN
            id = place.canteen_id
            print(f"{place_type}, {id}")
        elif isinstance(place, CinemaLocationTable):
            place_type = PlaceEnum.CINEMA
            id = place.cinema_id
            print(f"{place_type}, {id}")
        elif isinstance(place, BuildingLocationTable):
            place_type = PlaceEnum.BUILDING
            id = place.building_id
            print(f"{place_type}, {id}")
        else:
            raise ValueError(f"Invalid place type: {type(place)}")
        
        places_pydantic.append(
            Place(
                id=id,
                location=Location.from_table(place.location),
                type=place_type
            )
        )
    return places_pydantic