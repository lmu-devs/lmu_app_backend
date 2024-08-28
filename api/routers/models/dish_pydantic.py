

from api.models.dish_model import DishDatesDto, DishDateDto
from api.models.canteen_model import CanteenTable
from api.models.menu_model import MenuWeekTable


def dish_dates_to_pydantic(dish_id: str, menu_weeks: MenuWeekTable, canteens: CanteenTable) -> DishDatesDto:
    # look for dates where dish (dish_id) was available
    # look up in which canteens this dish was available for this date
    
    # return DishDatesDto
    pass

