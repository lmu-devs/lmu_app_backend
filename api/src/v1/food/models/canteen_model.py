from typing import List

from pydantic import BaseModel, RootModel

from shared.src.models import Rating, CanteenBase, Image, ActiveOpeningHours


class CanteenStatus(BaseModel):
    is_lecture_free: bool
    is_closed: bool
    is_temporary_closed: bool

class CanteenResponse(CanteenBase):
    status: CanteenStatus
    rating: Rating
    images: List[Image]
    opening_hours: ActiveOpeningHours
    
class Canteens(RootModel):
    root: List[CanteenResponse]

