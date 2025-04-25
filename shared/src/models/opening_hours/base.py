from datetime import time
from typing import List

from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.orm import Mapped, declared_attr, relationship

from shared.src.db.base_class import Base
from shared.src.enums.weekday_enum import WeekdayEnum
from shared.src.tables.time_range_table import TimeRange as BaseTimeRange


class BaseTimeRangeModel(Base, BaseTimeRange):
    """Base class for all time range models that inherit from the abstract TimeRange"""

    __abstract__ = True

    @declared_attr
    def opening_hours_id(cls):
        return Column(Integer, nullable=False)


class BaseOpeningHours:
    """Base class for all opening hours models"""

    id = Column(Integer, primary_key=True, index=True)
    weekday = Column(WeekdayEnum, nullable=False)
    is_closed = Column(Boolean, default=False)

    def add_time_range(self, start_time: time, end_time: time) -> BaseTimeRange:
        """Add a new time range to the opening hours."""
        time_range = self.time_range_class(opening_hours=self, start_time=start_time, end_time=end_time)
        self.time_ranges.append(time_range)
        return time_range

    @property
    def time_range_class(self):
        """Should be implemented by child classes to return their specific TimeRange class"""
        raise NotImplementedError
