from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums.canteen_enums import CanteenEnum, CanteenTypeEnum
from shared.src.models import ActiveOpeningHours, Images, Rating
from shared.src.models.location_model import Location
from shared.src.tables import CanteenStatusTable


class CanteenStatus(BaseModel):
    is_lecture_free: bool
    is_closed: bool
    is_temporary_closed: bool

    @classmethod
    def from_table(cls, status: CanteenStatusTable) -> "CanteenStatus":
        return CanteenStatus(
            is_lecture_free=status.is_lecture_free,
            is_closed=status.is_closed,
            is_temporary_closed=status.is_temporary_closed,
        )


class CanteenResponse(BaseModel):
    id: CanteenEnum
    name: str
    type: CanteenTypeEnum
    location: Location
    status: CanteenStatus
    rating: Rating
    images: Images
    opening_hours: ActiveOpeningHours


class Canteens(RootModel):
    root: List[CanteenResponse]
