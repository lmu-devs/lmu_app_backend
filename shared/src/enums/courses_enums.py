from enum import Enum


class CourseStartEnum(str, Enum):
    SINE_TEMPORE = "SINE_TEMPORE"
    CUM_TEMPORE = "CUM_TEMPORE"


class SemesterEnum(str, Enum):
    SUMMER = "SUMMER"
    WINTER = "WINTER"
