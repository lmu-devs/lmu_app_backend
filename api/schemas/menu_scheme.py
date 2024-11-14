from datetime import date
from typing import List
from pydantic import BaseModel, RootModel, field_validator

from api.schemas.dish_scheme import Dish


class MenuDay(BaseModel):
    date: date
    canteen_id: str
    dishes: List[Dish]
    
class Menus(RootModel):
    root: List[MenuDay]
    
    @field_validator('root')
    def sort_menu_days(cls, v):
        return sorted(v, key=lambda x: x.date)

    class Config:
        from_attributes = True