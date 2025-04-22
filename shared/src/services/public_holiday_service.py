from datetime import date

import holidays

from shared.src.core.logging import get_main_fetcher_logger
from shared.src.enums.language_enums import LanguageEnum

logger = get_main_fetcher_logger(__name__)


class PublicHolidayService:
    COUNTRY_MAPPING = {
        LanguageEnum.GERMAN: ("DE", "BY"),  # (country, state) tuple for Bavaria
        LanguageEnum.ENGLISH_US: ("US", None),  # No state specified for US
    }

    def __init__(self, language: LanguageEnum = LanguageEnum.GERMAN):
        """
        Initialize the holiday service based on language.
        Default is set to German (Bavaria) holidays.

        Args:
            language (LanguageEnum): The language enum determining the country
        """
        country_code, state_code = self.COUNTRY_MAPPING.get(language)
        logger.info(
            f"Initializing holiday service for language {language} (country: {country_code}, state: {state_code})"
        )
        self.country_holidays = holidays.country_holidays(country_code, subdiv=state_code)

    def is_university_holiday(self, check_date: date = None) -> bool:
        """Check if date falls within university holiday"""
        if check_date is None:
            check_date = date.today()
        return self.is_public_holiday(check_date) or self.is_christmas_break(check_date)

    def is_public_holiday(self, check_date=None) -> bool:
        """
        Check if a given date is a public holiday.
        If no date is provided, checks today's date.

        Args:
            check_date (date, optional): The date to check. Defaults to today.

        Returns:
            bool: True if the date is a public holiday, False otherwise
        """
        if check_date is None:
            check_date = date.today()

        return check_date in self.country_holidays

    def get_holiday_name(self, check_date=None) -> str | None:
        """
        Get the name of the holiday if it is a holiday.

        Args:
            check_date (date, optional): The date to check. Defaults to today.

        Returns:
            str | None: Name of the holiday, or None if it's not a holiday
        """
        if check_date is None:
            check_date = date.today()

        return self.country_holidays.get(check_date)

    def is_christmas_break(self, check_date: date) -> bool:
        """Check if date falls within Christmas break (Dec 24 - Jan 6)"""
        day = check_date.day
        month = check_date.month
        return (month == 12 and day >= 24) or (month == 1 and day <= 6)


if __name__ == "__main__":
    public_holiday_service = PublicHolidayService(LanguageEnum.GERMAN)
    print(public_holiday_service.is_university_holiday(date(2024, 12, 25)))
    print(public_holiday_service.get_holiday_name(date(2024, 12, 25)))
    print(public_holiday_service.is_public_holiday())
