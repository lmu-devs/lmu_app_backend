import uuid
from typing import Dict

from shared.src.tables import DishTable
from shared.src.schemas import Rating

from ..pydantics import canteen_to_pydantic
from ..schemas import Dish, DishDate, DishDates, DishPrice


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
                    user_likes_canteen=user_liked_canteens.get(canteen.id) if user_liked_canteens else None
                ) for canteen in canteens
            ]
        )
        for date, canteens in date_canteen_map.items()
    ]

    return DishDates(dates=dish_dates)


def dish_to_pydantic(dish: DishTable, user_id: uuid.UUID = None) -> Dish:

    title = dish.translations[0].title if dish.translations else "not translated"

    user_likes_dish = None
    if user_id:
        user_likes_dish = any(like.user_id == user_id for like in dish.likes)
        
    prices = [
        DishPrice(
            category=price.category,
            base_price=price.base_price or 0,
            price_per_unit=price.price_per_unit or 0,
            unit=price.unit or "None"
        )
        for price in dish.prices
    ]
    
    rating = Rating(
        like_count=dish.like_count,
        is_liked=user_likes_dish
    )

    return Dish(
        id=dish.id,
        title=title,
        dish_type=dish.dish_type,
        dish_category=dish.dish_category,
        labels=dish.labels,
        rating=rating,
        price_simple=dish.price_simple,
        prices=prices
    )
    

    
    
