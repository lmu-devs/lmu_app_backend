from datetime import time

from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import OpeningHour, OpeningHours, WeekdayEnum

benediktbeuren_opening_hours = {
    CanteenEnum.STUBISTRO_BENEDIKTBEUREN: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 45), end_time=time(13, 45)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 45), end_time=time(13, 45)),
            OpeningHour(
                day=WeekdayEnum.WEDNESDAY,
                start_time=time(11, 45),
                end_time=time(13, 45),
            ),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 45), end_time=time(13, 45)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 45), end_time=time(13, 45)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
        lecture_free_hours=None,
    ),
}
