from shared.src.schemas import (Canteen, Image, OpeningHours, Rating,
                                WeekdayEnum)
from shared.src.tables import CanteenTable

from ...core.pydantics.location_pydantic import location_to_pydantic


def canteen_to_pydantic(canteen: CanteenTable, user_likes_canteen: bool = None) -> Canteen:
    location = location_to_pydantic(canteen.location)

    day_mapping = {
        'mon': WeekdayEnum.MONDAY,
        'tue': WeekdayEnum.TUESDAY,
        'wed': WeekdayEnum.WEDNESDAY,
        'thu': WeekdayEnum.THURSDAY,
        'fri': WeekdayEnum.FRIDAY,
        'sat': WeekdayEnum.SATURDAY,
        'sun': WeekdayEnum.SUNDAY
    }

    opening_hours = []
    for oh in canteen.opening_hours:
        weekday = day_mapping.get(oh.day)
        if weekday:
            opening_hours.append(OpeningHours(
                day=weekday,
                start_time=oh.start_time,
                end_time=oh.end_time
            ))
    
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
        

    return Canteen(
        id=canteen.id,
        name=canteen.name,
        type=canteen.type,
        rating=rating,
        location=location,
        opening_hours=opening_hours,
        images=images
    )