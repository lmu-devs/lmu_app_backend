import uuid
from typing import List

from shared.models.menu_model import MenuDayTable
from api.schemas.menu_scheme import MenuDay, Menus
from .dish_pydantic import dish_to_pydantic


def menu_day_to_pydantic(menu_day: MenuDayTable, user_id: uuid.UUID = None) -> MenuDay:
    dishes_dto = [
        dish_to_pydantic(
            association.dish,
            user_id=user_id
        )
        for association in menu_day.dish_associations
    ]
        
    return MenuDay(
        date=menu_day.date,
        canteen_id=menu_day.canteen_id,
        dishes=dishes_dto
    )

def menu_days_to_pydantic(menu_days: List[MenuDayTable], user_id: uuid.UUID = None) -> Menus:
    return Menus(root=[
        menu_day_to_pydantic(menu_day, user_id) 
        for menu_day in menu_days
    ])
