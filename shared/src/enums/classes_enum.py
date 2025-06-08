from enum import Enum


class LectureStartTypeEnum(str, Enum):
    SINE_TEMPORE = "SINE_TEMPORE"
    CUM_TEMPORE = "CUM_TEMPORE"


class SemesterTypeEnum(str, Enum):
    SUMMER_SEMESTER = "SOSE"
    WINTER_SEMESTER = "WISE"
