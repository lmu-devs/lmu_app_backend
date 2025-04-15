from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo


class TimezoneManager:
    DEFAULT_TIMEZONE = "Europe/Berlin"

    @classmethod
    def now(cls, timezone: Optional[str] = None) -> datetime:
        """Get current datetime in specified timezone (defaults to Berlin)"""
        tz = timezone or cls.DEFAULT_TIMEZONE
        return datetime.now(tz=ZoneInfo(tz))

    @classmethod
    def now_date(cls) -> date:
        """Get current date in specified timezone (defaults to Berlin)"""
        return cls.now().date()

    @classmethod
    def convert_to_timezone(cls, dt: datetime, timezone: Optional[str] = None) -> datetime:
        """Convert a datetime object to specified timezone (defaults to Berlin)"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        target_tz = timezone or cls.DEFAULT_TIMEZONE
        return dt.astimezone(ZoneInfo(target_tz))

    @classmethod
    def get_timezone(cls, timezone: Optional[str] = None) -> ZoneInfo:
        """Get ZoneInfo object for specified timezone (defaults to Berlin)"""
        return ZoneInfo(timezone or cls.DEFAULT_TIMEZONE)
