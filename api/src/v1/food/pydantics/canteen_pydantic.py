from api.src.v1.food.models.canteen_model import CanteenResponse, CanteenStatus
from shared.src.enums import OpeningHoursTypeEnum
from shared.src.models import ActiveOpeningHours, OpeningHour, Rating
from shared.src.models.image_model import Images
from shared.src.models.location_model import Location
from shared.src.tables import CanteenTable


def canteen_to_pydantic(canteen: CanteenTable) -> CanteenResponse:
    location = Location.from_table(canteen.location)
    # If user_id was provided, check if there are any likes for this user
    is_liked = bool(canteen.likes)
    rating = Rating.from_params(like_count=canteen.like_count, is_liked=is_liked)
    images = Images.from_table(canteen.images)
    status = CanteenStatus.from_table(canteen.status)

    
    # Group opening hours by type
    opening_hours_dict = {
        OpeningHoursTypeEnum.OPENING_HOURS: [],
        OpeningHoursTypeEnum.SERVING_HOURS: [],
        OpeningHoursTypeEnum.LECTURE_FREE_HOURS: [],
        OpeningHoursTypeEnum.LECTURE_FREE_SERVING_HOURS: []
    }
    
    for hour in canteen.opening_hours:
        opening_hour = OpeningHour.from_table(hour)
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