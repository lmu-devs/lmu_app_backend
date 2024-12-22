from typing import List

from pydantic import RootModel

from shared.src.schemas import Image, Rating, Canteen


class CanteenResponse(Canteen):
    is_lecture_free: bool
    is_closed: bool
    is_temporary_closed: bool
    rating: Rating
    images: List[Image]
    
class Canteens(RootModel):
    root: List[CanteenResponse]

