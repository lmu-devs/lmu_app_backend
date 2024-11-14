import uuid
from typing import List
from api.models.menu_model import MenuDayDto, MenuDayTable, MenusDto
from api.routers.models.dish_pydantic import dish_to_pydantic

def menu_day_to_pydantic(menu_day: MenuDayTable, user_id: uuid.UUID = None) -> MenuDayDto:
    dishes_dto = [
        dish_to_pydantic(
            association.dish,
            user_id=user_id
        )
        for association in menu_day.dish_associations
    ]
        
    return MenuDayDto(
        date=menu_day.date,
        canteen_id=menu_day.canteen_id,
        dishes=dishes_dto
    )

def menu_days_to_pydantic(menu_days: List[MenuDayTable], user_id: uuid.UUID = None) -> MenusDto:
    return MenusDto(root=[
        menu_day_to_pydantic(menu_day, user_id) 
        for menu_day in menu_days
    ])
