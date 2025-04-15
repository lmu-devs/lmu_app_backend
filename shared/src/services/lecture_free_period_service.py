from datetime import date, timedelta
from enum import Enum
from typing import Tuple

from shared.src.core.logging import get_food_fetcher_logger
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.public_holiday_service import PublicHolidayService

logger = get_food_fetcher_logger(__name__)


class Semester(Enum):
    WINTER = "Winter"
    SUMMER = "Summer"


class LectureFreePeriodService:
    def __init__(self, language: LanguageEnum = LanguageEnum.GERMAN):
        """
        Initialize the lecture-free period service.

        Args:
            language (LanguageEnum): Language setting for holiday detection
        """
        self.public_holiday_service = PublicHolidayService(language)

    def _get_semester_dates(self, year: int, semester: Semester) -> Tuple[date, date]:
        """
        Calculate semester start and end dates.

        Winter semester: Starts on first workday of second-to-last full week of October
        Summer semester: Starts on first workday of second-to-last or third-to-last full week of April

        Winter semester duration: 16 weeks
        Summer semester duration: 14 weeks
        """
        if semester == Semester.WINTER:
            # Find the last Monday of October
            last_day = date(year, 11, 1) - timedelta(days=1)
            last_monday = last_day - timedelta(days=(last_day.weekday()))
            start_date = last_monday - timedelta(weeks=1)
            end_date = start_date + timedelta(weeks=16)
        else:  # SUMMER
            # Find the last Monday of April
            last_day = date(year, 5, 1) - timedelta(days=1)
            last_monday = last_day - timedelta(days=(last_day.weekday()))
            start_date = last_monday - timedelta(weeks=2)  # Third-to-last week
            end_date = start_date + timedelta(weeks=14)

        return start_date, end_date

    def is_lecture_free(self, check_date: date = None) -> bool:
        """
        Check if a given date is lecture-free.

        Args:
            check_date (date, optional): Date to check. Defaults to today.

        Returns:
            bool: True if the date is lecture-free, False otherwise
        """
        if check_date is None:
            check_date = date.today()

        # Determine current semester
        if 4 <= check_date.month <= 9:  # Summer semester period
            start_date, end_date = self._get_semester_dates(check_date.year, Semester.SUMMER)
        else:  # Winter semester period
            if check_date.month < 4:  # First months belong to previous year's winter semester
                start_date, end_date = self._get_semester_dates(check_date.year - 1, Semester.WINTER)
            else:
                start_date, end_date = self._get_semester_dates(check_date.year, Semester.WINTER)

        # Check if date is outside lecture period
        is_free = not (start_date <= check_date <= end_date)
        return is_free


if __name__ == "__main__":
    service = LectureFreePeriodService()
    print(service._get_semester_dates(2024, Semester.WINTER))
    print(service._get_semester_dates(2025, Semester.SUMMER))
    today = date.today()
    another_date = date(2025, 2, 11)
    print(f"Is today ({today}) lecture-free? {service.is_lecture_free()}")
    print(f"Is another date ({another_date}) lecture-free? {service.is_lecture_free(another_date)}")
