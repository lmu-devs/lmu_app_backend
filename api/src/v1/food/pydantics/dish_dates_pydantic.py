from typing import Dict

from api.src.v1.food.models import DishDate, DishDates
from api.src.v1.food.pydantics import canteen_to_pydantic


def dish_dates_to_pydantic(results, user_liked_canteens: Dict[str, bool] = None) -> DishDates:
    date_canteen_map = {}
    for date, canteen_id, canteen in results:
        if date not in date_canteen_map:
            date_canteen_map[date] = []
        date_canteen_map[date].append(canteen)

    dish_dates = [
        DishDate(
            date=date,
            canteens=[
                canteen_to_pydantic(
                    canteen,
                    user_likes_canteen=(user_liked_canteens.get(canteen.id) if user_liked_canteens else None),
                )
                for canteen in canteens
            ],
        )
        for date, canteens in date_canteen_map.items()
    ]

    return DishDates(dates=dish_dates)
