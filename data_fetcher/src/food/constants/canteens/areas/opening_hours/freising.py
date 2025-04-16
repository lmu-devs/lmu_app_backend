from datetime import time

from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import OpeningHour, OpeningHours, WeekdayEnum

freising_opening_hours = {
    CanteenEnum.MENSA_WEIHENSTEPHAN: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(13, 30)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
        lecture_free_hours=None,
    ),
    CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(15, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(15, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(15, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(15, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(14, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(14, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 0), end_time=time(14, 30)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 0), end_time=time(14, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(10, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(10, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(10, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(10, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 0), end_time=time(13, 30)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 30), end_time=time(13, 30)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 30), end_time=time(13, 30)),
            OpeningHour(
                day=WeekdayEnum.WEDNESDAY,
                start_time=time(11, 30),
                end_time=time(13, 30),
            ),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 30), end_time=time(13, 30)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
        lecture_free_hours=None,
    ),
    # CanteenEnum.STULOUNGE_WEIHENSTEPHAN: OpeningHours(
    #     opening_hours=[
    #         OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(7, 45), end_time=time(14, 30)),
    #         OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(7, 45), end_time=time(14, 30)),
    #         OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(7, 45), end_time=time(14, 30)),
    #         OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(7, 45), end_time=time(14, 30)),
    #         OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(7, 45), end_time=time(13, 0)),
    #     ],
    #     lecture_free_hours=[
    #         OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 0), end_time=time(13, 0)),
    #     ],
    #     serving_hours=None,
    #     lecture_free_serving_hours=None,
    # ),
}
