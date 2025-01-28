from typing import List
from uuid import UUID
from pydantic import BaseModel, RootModel

from shared.src.models import Rating
from shared.src.tables import DishTable
from .dish_price_model import DishPrices

class Dish(BaseModel):
    id: UUID
    title: str
    dish_type: str
    dish_category: str
    price_simple: str | None = None
    prices: DishPrices
    rating: Rating
    labels: List[str]
    
    @classmethod
    def from_table(cls, dish: DishTable, user_id: UUID = None) -> 'Dish':

        title = dish.translations[0].title if dish.translations else "not translated"

        user_likes_dish = None
        if user_id:
            user_likes_dish = any(like.user_id == user_id for like in dish.likes)
            
        rating = Rating.from_params(like_count=dish.like_count, is_liked=user_likes_dish)
        
        prices = DishPrices.from_table(dish.prices)

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

    
class Dishes(RootModel):
    root: List[Dish]
