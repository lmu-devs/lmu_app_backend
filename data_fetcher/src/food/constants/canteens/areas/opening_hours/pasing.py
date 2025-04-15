from datetime import time

from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import OpeningHour, OpeningHours, WeekdayEnum

pasing_opening_hours = {
    CanteenEnum.MENSA_PASING: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
        lecture_free_hours=None,
    ),
    CanteenEnum.STUCAFE_PASING: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 30)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
}
