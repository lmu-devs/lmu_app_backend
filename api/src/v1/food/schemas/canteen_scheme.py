from typing import List

from pydantic import BaseModel, RootModel

from shared.src.schemas import Rating, Canteen, Image


class CanteenStatus(BaseModel):
    is_lecture_free: bool
    is_closed: bool
    is_temporary_closed: bool

class CanteenResponse(Canteen):
    status: CanteenStatus
    rating: Rating
    images: List[Image]
    
class Canteens(RootModel):
    root: List[CanteenResponse]

