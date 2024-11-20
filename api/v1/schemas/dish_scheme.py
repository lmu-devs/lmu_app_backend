from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from api.v1.schemas.canteen_scheme import Canteen
from api.v1.schemas.rating_scheme import Rating


class DishPrice(BaseModel):
    category: str
    base_price: float
    price_per_unit: float
    unit: str
    
class Dish(BaseModel):
    id: int
    title: str
    dish_type: str
    rating: Rating
    price_simple: Optional[str] = None
    labels: List[str]
    prices: List[DishPrice]
    
class Dishes(BaseModel):
    dishes: List[Dish]
    

class DishDate(BaseModel):
    date: date
    canteens: List[Canteen]

class DishDates(BaseModel):
    dates: List[DishDate]