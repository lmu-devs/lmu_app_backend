from api.models.canteen_model import CanteenDto, CanteenTable, LocationDto, OpeningHoursDto, Weekday
from api.models.rating_model import RatingDto


def canteen_to_pydantic(canteen: CanteenTable, user_likes_canteen: bool = None) -> CanteenDto:
    location = LocationDto(
        address=canteen.location.address,
        latitude=float(canteen.location.latitude),
        longitude=float(canteen.location.longitude)
    )

    day_mapping = {
        'mon': Weekday.MONDAY,
        'tue': Weekday.TUESDAY,
        'wed': Weekday.WEDNESDAY,
        'thu': Weekday.THURSDAY,
        'fri': Weekday.FRIDAY,
        'sat': Weekday.SATURDAY,
        'sun': Weekday.SUNDAY
    }

    opening_hours = []
    for oh in canteen.opening_hours:
        weekday = day_mapping.get(oh.day)
        if weekday:
            opening_hours.append(OpeningHoursDto(
                day=weekday,
                start_time=oh.start_time,
                end_time=oh.end_time
            ))
    
    like_count_value = canteen.like_count
    
    rating = RatingDto(
        like_count=like_count_value, 
        is_liked=user_likes_canteen
        )

    return CanteenDto(
        id=canteen.id,
        name=canteen.name,
        rating=rating,
        location=location,
        opening_hours=opening_hours
    )