from app.models.canteen_model import CanteenDto, CanteenTable, LocationDto, OpeningHoursDto, Weekday


def canteen_to_pydantic(canteen: CanteenTable) -> CanteenDto:
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

    return CanteenDto(
        canteen_id=canteen.canteen_id,
        name=canteen.name,
        location=location,
        opening_hours=opening_hours 
    )