import uuid
from api.models.menu_model import MenuDayDto, MenuWeekDto, MenuWeekTable, MenusDto

from api.routers.models.dish_pydantic import dish_to_pydantic



def menu_week_to_pydantic(menu_week: MenuWeekTable, user_id: uuid.UUID = None) -> MenusDto:
    menu_days = []
    for menu_day in menu_week.menu_days:
        
        dishes_dto = [
            dish_to_pydantic(
                association.dish,
                user_id=user_id
            )
            for association in menu_day.dish_associations
        ]
            
        menu_days.append(MenuDayDto(
            date=menu_day.date,
            dishes=dishes_dto
        ))
    
    return MenuWeekDto(
        week=menu_week.week,
        year=menu_week.year,
        canteen_id=menu_week.canteen_id,
        menu_days=menu_days
    )
