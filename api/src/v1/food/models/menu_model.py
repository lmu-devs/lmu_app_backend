from datetime import date
from typing import List
from pydantic import BaseModel, RootModel, field_validator

from . import Dish


class MenuDay(BaseModel):
    date: date
    canteen_id: str
    is_closed: bool
    dishes: List[Dish]
    
class Menus(RootModel):
    root: List[MenuDay]
    
    @field_validator('root')
    def sort_menu_days(cls, v):
        return sorted(v, key=lambda x: x.date)

    class ConfigDict:
        from_attributes = True