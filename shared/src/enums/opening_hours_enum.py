from enum import Enum


class OpeningHoursTypeEnum(str, Enum):
    OPENING_HOURS = "opening_hours"
    SERVING_HOURS = "serving_hours"
    LECTURE_FREE_HOURS = "lecture_free_hours"
    LECTURE_FREE_SERVING_HOURS = "lecture_free_serving_hours"
