from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import CanteenEnum


class Canteen(BaseModel):
    id: CanteenEnum
    url_id: int | None = None


class Canteens(RootModel):
    root: List[Canteen]
