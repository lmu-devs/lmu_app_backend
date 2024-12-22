from datetime import date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from shared.src.schemas import Rating

from ..schemas import CanteenResponse


class DishPrice(BaseModel):
    category: str
    base_price: float
    price_per_unit: float
    unit: str
    
class Dish(BaseModel):
    id: UUID
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
    canteens: List[CanteenResponse]

class DishDates(BaseModel):
    dates: List[DishDate]