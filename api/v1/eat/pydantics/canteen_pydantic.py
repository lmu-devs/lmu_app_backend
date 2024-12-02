from shared.tables.canteen_table import CanteenTable
from ..schemas import Canteen, Location, Weekday, OpeningHours, Image
from api.v1.core.schemas.rating_scheme import Rating


def canteen_to_pydantic(canteen: CanteenTable, user_likes_canteen: bool = None) -> Canteen:
    location = Location(
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