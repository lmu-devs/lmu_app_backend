from datetime import time

from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import OpeningHour, OpeningHours, WeekdayEnum

garching_opening_hours = {
    CanteenEnum.MENSA_GARCHING: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(10, 45), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(10, 45), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(10, 45), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(10, 45), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 45), end_time=time(14, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(16, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(16, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(16, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(16, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(15, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(15, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.ESPRESSOBAR_GARCHING_APE: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 30), end_time=time(14, 30)),
            OpeningHour(
                day=WeekdayEnum.WEDNESDAY,
                start_time=time(11, 30),
                end_time=time(14, 30),
            ),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 30), end_time=time(14, 30)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(15, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(15, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.ESPRESSOBAR_GARCHING: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(7, 30), end_time=time(18, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(7, 30), end_time=time(18, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(7, 30), end_time=time(18, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(7, 30), end_time=time(18, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(7, 30), end_time=time(15, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
        lecture_free_hours=None,
    ),
}
