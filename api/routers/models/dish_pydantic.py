from sqlalchemy.orm import Session

from api.models.dish_model import DishDatesDto, DishDateDto
from api.models.canteen_model import CanteenTable, Weekday
from api.models.menu_model import MenuDayTable, MenuDishAssociation
from api.routers.models.canteen_pydantic import canteen_to_pydantic


def dish_dates_to_pydantic(db: Session, dish_id: int) -> DishDatesDto:
    # Query to get all dates and canteens where the dish was available
    
    query = (
        db.query(
            MenuDishAssociation.menu_day_date,
            MenuDayTable.menu_week_canteen_id,
            CanteenTable
        )
        .join(MenuDayTable, MenuDishAssociation.menu_day_date == MenuDayTable.date)
        .join(CanteenTable, MenuDayTable.menu_week_canteen_id == CanteenTable.canteen_id)
        .filter(MenuDishAssociation.dish_id == dish_id)
        .order_by(MenuDishAssociation.menu_day_date)
    )

    results = query.all()

    date_canteen_map = {}
    for date, canteen_id, canteen in results:
        if date not in date_canteen_map:
            date_canteen_map[date] = []
        date_canteen_map[date].append(canteen)

    dish_dates = [
        DishDateDto(
            date=date,
            canteens=[canteen_to_pydantic(canteen) for canteen in canteens]
        )
        for date, canteens in date_canteen_map.items()
    ]

    return DishDatesDto(dates=dish_dates)
