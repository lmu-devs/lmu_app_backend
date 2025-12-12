from pydantic import BaseModel

from shared.src.enums.courses_enums import SemesterEnum
from shared.src.services.lecture_free_period_service import LectureFreePeriodService


class SemesterModel(BaseModel):
    year: int
    semester_type: SemesterEnum


def get_current_semester() -> SemesterModel:
    """
    Calculate the current semester based on today's date.

    Uses the LectureFreePeriodService for the calculation.
    """
    service = LectureFreePeriodService()
    current = service.get_current_semester()
    return SemesterModel(year=current.year, semester_type=current.semester_type)


class SemestersModel(BaseModel):
    semesters: list[SemesterModel]
    current_semester: SemesterModel = None

    def __init__(self, **data):
        if data.get("current_semester") is None:
            data["current_semester"] = get_current_semester()
        super().__init__(**data)
