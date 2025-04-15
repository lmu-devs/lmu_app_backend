from datetime import date

from shared.src.models.opening_hour_model import OpeningHours
from shared.src.services.lecture_free_period_service import LectureFreePeriodService
from shared.src.services.public_holiday_service import PublicHolidayService


class CanteenOpeningStatusService:
    _lecture_free_period_service = LectureFreePeriodService()
    _public_holiday_service = PublicHolidayService()

    @classmethod
    def is_lecture_free(cls, check_date: date = None) -> bool:
        return cls._lecture_free_period_service.is_lecture_free(check_date)

    @classmethod
    def is_closed(cls, check_date: date = None) -> bool:
        if check_date is None:
            check_date = date.today()
        if cls._public_holiday_service.is_university_holiday(check_date):
            return True
        return False

    @classmethod
    def is_temp_closed(cls, opening_hours: OpeningHours) -> bool:
        if opening_hours.opening_hours or opening_hours.lecture_free_hours:
            return False
        return True
