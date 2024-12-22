from shared.src.enums.opening_hours_enum import OpeningHoursTypeEnum
from shared.src.schemas import (Image, OpeningHour, OpeningHours,
                                Rating)
from shared.src.tables import CanteenTable, CanteenStatusTable


from ..schemas import CanteenResponse
from ...core.pydantics.location_pydantic import location_to_pydantic


def canteen_to_pydantic(canteen: CanteenTable, user_likes_canteen: bool = None) -> CanteenResponse:
    location = location_to_pydantic(canteen.location)

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
    
    opening_hours = OpeningHours(
        opening_hours=opening_hours_dict[OpeningHoursTypeEnum.OPENING_HOURS] or None,
        serving_hours=opening_hours_dict[OpeningHoursTypeEnum.SERVING_HOURS] or None,
        lecture_free_hours=opening_hours_dict[OpeningHoursTypeEnum.LECTURE_FREE_HOURS] or None,
        lecture_free_serving_hours=opening_hours_dict[OpeningHoursTypeEnum.LECTURE_FREE_SERVING_HOURS] or None
    )
    
    like_count_value = canteen.like_count
    
    rating = Rating(
        like_count=like_count_value, 
        is_liked=user_likes_canteen
        )
    
    images = []
    for image in canteen.images:
        image_dto = Image(
            url=image.url,
            name=image.name
        )
        images.append(image_dto)
        
    status : CanteenStatusTable = canteen.status
    print(status.__repr__())
        

    return CanteenResponse(
        id=canteen.id,
        name=canteen.name,
        type=canteen.type,
        is_lecture_free=status.is_lecture_free,
        is_closed=status.is_closed,
        is_temporary_closed=status.is_temporary_closed,
        rating=rating,
        location=location,
        opening_hours=opening_hours,
        images=images
    )