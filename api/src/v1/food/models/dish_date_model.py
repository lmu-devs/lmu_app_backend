from datetime import date
from typing import List
from pydantic import BaseModel, RootModel

from . import CanteenResponse


class DishDate(BaseModel):
    date: date
    canteens: List[CanteenResponse]

class DishDates(RootModel):
    root: List[DishDate]