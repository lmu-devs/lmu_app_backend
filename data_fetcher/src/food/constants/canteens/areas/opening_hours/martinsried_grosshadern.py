from datetime import time

from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import OpeningHour, OpeningHours, WeekdayEnum

martinsried_grosshadern_opening_hours = {
    CanteenEnum.MENSA_MARTINSRIED: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
        ],
        serving_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(13, 30)),
        ],
        lecture_free_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.STUBISTRO_MARTINSRIED: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(14, 30)),
        ],
        serving_hours=None,
        lecture_free_hours=None,
        lecture_free_serving_hours=None,
    ),
    # CanteenEnum.STULOUNGE_MARTINSRIED: OpeningHours(
    #     opening_hours=[
    #         OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 30), end_time=time(16, 30)),
    #         OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 30), end_time=time(16, 30)),
    #         OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 30), end_time=time(16, 30)),
    #         OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 30), end_time=time(16, 30)),
    #         OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 30), end_time=time(15, 30)),
    #     ],
    #     serving_hours=None,
    #     lecture_free_hours=None,
    #     lecture_free_serving_hours=None,
    # ),
    CanteenEnum.ESPRESSOBAR_MARTINSRIED: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(16, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(15, 0)),
        ],
        serving_hours=None,
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(14, 0)),
        ],
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.STUBISTRO_BUTENANDSTR: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(14, 0)),
        ],
        serving_hours=None,
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
        ],
        lecture_free_serving_hours=None,
    ),
    # CanteenEnum.STULOUNGE_BUTENANDSTR: OpeningHours(
    #     opening_hours=None,
    #     serving_hours=None,
    #     lecture_free_hours=None,
    #     lecture_free_serving_hours=None,
    # ),
}
