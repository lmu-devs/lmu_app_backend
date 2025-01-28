from shared.src.models.location_model import Location

from api.src.v1.food.models.canteen_model import (CanteenResponse,
                                                    CanteenStatus)
from shared.src.enums import OpeningHoursTypeEnum
from shared.src.models.image_model import Images
from shared.src.models import OpeningHour, ActiveOpeningHours, Rating
from shared.src.tables import CanteenTable


def canteen_to_pydantic(canteen: CanteenTable, user_likes_canteen: bool = None) -> CanteenResponse:
    location = Location.from_table(canteen.location)

    status = CanteenStatus(
        is_lecture_free=canteen.status.is_lecture_free,
        is_closed=canteen.status.is_closed,
        is_temporary_closed=canteen.status.is_temporary_closed
    )
    
    # Group opening hours by type
    opening_hours_dict = {
        OpeningHoursTypeEnum.OPENING_HOURS: [],
        OpeningHoursTypeEnum.SERVING_HOURS: [],
        OpeningHoursTypeEnum.LECTURE_FREE_HOURS: [],
        OpeningHoursTypeEnum.LECTURE_FREE_SERVING_HOURS: []
    }
    
    for hour in canteen.opening_hours:
        opening_hour = OpeningHour(
            day=hour.day,
            start_time=hour.start_time,
            end_time=hour.end_time
        )
        opening_hours_dict[hour.type].append(opening_hour)
    
    if canteen.status.is_lecture_free:
        opening_hours = ActiveOpeningHours(
            opening_hours=opening_hours_dict[OpeningHoursTypeEnum.LECTURE_FREE_HOURS] or [],
            serving_hours=opening_hours_dict[OpeningHoursTypeEnum.LECTURE_FREE_SERVING_HOURS] or [],
        )
    else:
        opening_hours = ActiveOpeningHours(
            opening_hours=opening_hours_dict[OpeningHoursTypeEnum.OPENING_HOURS] or [],
            serving_hours=opening_hours_dict[OpeningHoursTypeEnum.SERVING_HOURS] or [],
        )
    
    rating = Rating(
        like_count=canteen.like_count, 
        is_liked=user_likes_canteen
    )
    
    images = Images.from_table(canteen.images)

    return CanteenResponse(
        id=canteen.id,
        name=canteen.name,
        type=canteen.type,
        status=status,
        rating=rating,
        location=location,
        opening_hours=opening_hours,
        images=images
    )