from data_fetcher.src.food.constants.canteens.areas.locations import (
    benediktbeuren_locations,
    freising_locations,
    garching_locations,
    martinsried_grosshadern_locations,
    munich_locations,
    oberschleissheim_locations,
    pasing_locations,
    rosenheim_locations,
)
from shared.src.enums import CanteenEnum
from shared.src.models import Location


class CanteenLocationsConstants:
    @classmethod
    def get_location(cls, canteen_enum: CanteenEnum) -> Location:
        return cls._locations[canteen_enum]

    @classmethod
    def get_all_locations(cls) -> dict[CanteenEnum, Location]:
        return cls._locations

    _locations = {
        **munich_locations,
        **martinsried_grosshadern_locations,
        **garching_locations,
        **pasing_locations,
        **rosenheim_locations,
        **oberschleissheim_locations,
        **freising_locations,
        **benediktbeuren_locations,
    }
