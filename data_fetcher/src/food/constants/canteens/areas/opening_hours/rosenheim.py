from datetime import time

from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import OpeningHour, OpeningHours, WeekdayEnum

rosenheim_opening_hours = {
    CanteenEnum.MENSA_ROSENHEIM: OpeningHours(
        opening_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 15), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 15), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 15), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 15), end_time=time(15, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 15), end_time=time(14, 0)),
        ],
        lecture_free_hours=[
            OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
            OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
        ],
        serving_hours=None,
        lecture_free_serving_hours=None,
    ),
    # CanteenEnum.STULOUNGE_ROSENHEIM: OpeningHours(
    #     opening_hours=[
    #         OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 0), end_time=time(15, 0)),
    #         OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 0), end_time=time(15, 0)),
    #         OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 0), end_time=time(15, 0)),
    #         OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 0), end_time=time(15, 0)),
    #         OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 0), end_time=time(15, 0)),
    #     ],
    #     lecture_free_hours=[
    #         OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(10, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(10, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(10, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(10, 0), end_time=time(14, 0)),
    #         OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 0), end_time=time(14, 0)),
    #     ],
    #     serving_hours=None,
    #     lecture_free_serving_hours=None,
    # ),
}
