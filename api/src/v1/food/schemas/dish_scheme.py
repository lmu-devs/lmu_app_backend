from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from ..schemas import Canteen
from api.src.v1.core import Rating


class DishPrice(BaseModel):
    category: str
    base_price: float
    price_per_unit: float
    unit: str
    
class Dish(BaseModel):
    id: int
    title: str
    dish_type: str
    dish_category: str
    price_simple: Optional[str] = None
    prices: List[DishPrice]
    rating: Rating
    labels: List[str]
    
class Dishes(BaseModel):
    dishes: List[Dish]
    

class DishDate(BaseModel):
    date: date
    canteens: List[Canteen]

class DishDates(BaseModel):
    dates: List[DishDate]