from shared.src.models import Location
from shared.src.enums import CanteenEnum
from data_fetcher.src.food.constants.canteens.areas.locations import munich_locations, martinsried_grosshadern_locations, garching_locations, pasing_locations, rosenheim_locations, oberschleissheim_locations, freising_locations, benediktbeuren_locations

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
    