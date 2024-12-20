from shared.src.schemas import OpeningHours
from shared.src.enums.canteen_enums import CanteenEnum
from data_fetcher.src.food.constants.canteens.areas.opening_hours import munich_opening_hours, martinsried_grosshadern_opening_hours, garching_opening_hours, pasing_opening_hours, rosenheim_opening_hours, oberschleissheim_opening_hours, freising_opening_hours

class CanteenOpeningHoursConstants:
    @classmethod
    def get_opening_hours(cls, canteen_enum: CanteenEnum) -> OpeningHours:
        return cls._opening_hours[canteen_enum]
    
    @classmethod
    def get_all_opening_hours(cls) -> dict[CanteenEnum, OpeningHours]:
        return cls._opening_hours
    
    _opening_hours = {
        **munich_opening_hours,
        **martinsried_grosshadern_opening_hours,
        **garching_opening_hours,
        **pasing_opening_hours,
        **rosenheim_opening_hours,
        **oberschleissheim_opening_hours,
        **freising_opening_hours
    }
    



