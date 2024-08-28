from app.models.dish_model import DishPriceDto, DishDto
from app.models.menu_model import MenuDayDto, MenuWeekDto, MenuWeekTable



def menu_week_to_pydantic(menu_week: MenuWeekTable) -> MenuWeekDto:
    menu_days = []
    for menu_day in menu_week.menu_days:
        dishes = []
        for dish in menu_day.dishes:
            prices = [
                DishPriceDto(
                    category=price.category,
                    base_price=price.base_price,
                    price_per_unit=price.price_per_unit,
                    unit=price.unit
                )
                for price in dish.prices
            ]
            dishes.append(DishDto(
                name=dish.name,
                dish_type=dish.dish_type,
                labels=dish.labels,
                prices=prices
            ))
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