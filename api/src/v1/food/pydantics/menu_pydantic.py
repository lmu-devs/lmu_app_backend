import uuid
from typing import List

from shared.src.tables import MenuDayTable

from api.src.v1.food.models import MenuDay, Menus, Dish


def menu_day_to_pydantic(menu_day: MenuDayTable, user_id: uuid.UUID = None) -> MenuDay:
    dishes_dto = [
        Dish.from_table(
            association.dish,
            user_id=user_id
        )
        for association in menu_day.dish_associations
    ]
        
    return MenuDay(
        date=menu_day.date,
        canteen_id=menu_day.canteen_id,
        is_closed=menu_day.is_closed,
        dishes=dishes_dto
    )

def menu_days_to_pydantic(menu_days: List[MenuDayTable], user_id: uuid.UUID = None) -> Menus:
    return Menus(root=[
        menu_day_to_pydantic(menu_day, user_id) 
        for menu_day in menu_days
    ])
