from typing import Dict
import uuid

from api.models.dish_model import DishDatesDto, DishDateDto, DishDto, DishPriceDto, DishTable
from api.models.rating_model import RatingDto
from api.routers.models.canteen_pydantic import canteen_to_pydantic


def dish_dates_to_pydantic(results, user_liked_canteens: Dict[str, bool] = None) -> DishDatesDto:
    date_canteen_map = {}
    for date, canteen_id, canteen in results:
        if date not in date_canteen_map:
            date_canteen_map[date] = []
        date_canteen_map[date].append(canteen)

    dish_dates = [
        DishDateDto(
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

    return DishDatesDto(dates=dish_dates)



def dish_to_pydantic(dish: DishTable, user_id: uuid.UUID = None) -> DishDto:


    user_likes_dish = None
    if user_id:
        user_likes_dish = any(like.user_id == user_id for like in dish.likes)
    

    prices = [
        DishPriceDto(
            category=price.category,
            base_price=price.base_price,
            price_per_unit=price.price_per_unit,
            unit=price.unit
        )
        for price in dish.prices
    ]
    
    rating = RatingDto(
        like_count=dish.like_count,
        is_liked=user_likes_dish
    )

    return DishDto(
        id=dish.id,
        name=dish.name,
        dish_type=dish.dish_type,
        labels=dish.labels,
        rating=rating,
        price_simple=dish.price_simple,
        prices=prices
    )
    

    
    
