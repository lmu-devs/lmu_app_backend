from api.models.menu_model import MenuDayDto, MenuWeekDto, MenuWeekTable
from api.routers.models.dish_pydantic import dish_to_pydantic



def menu_week_to_pydantic(menu_week: MenuWeekTable) -> MenuWeekDto:
    menu_days = []
    for menu_day in menu_week.menu_days:
        
        dishes = []
        for association in menu_day.dish_associations:
            dish = association.dish
            dish_pydantic = dish_to_pydantic(dish)
            dishes.append(dish_pydantic)
            
        menu_days.append(MenuDayDto(
            date=menu_day.date,
            dishes=dishes
        ))
    
    return MenuWeekDto(
        week=menu_week.week,
        year=menu_week.year,
        canteen_id=menu_week.canteen_id,
        menu_days=menu_days
    )
