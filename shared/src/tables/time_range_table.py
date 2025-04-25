from sqlalchemy import Column, Time
from sqlalchemy.ext.declarative import declared_attr

from shared.src.core.database import Base


class TimeRange(Base):
    """
    Abstract base class for time range.
    Declares a time range column.
    """

    __abstract__ = True

    @declared_attr
    def start_time(cls):
        return Column(Time, nullable=False)

    @declared_attr
    def end_time(cls):
        return Column(Time, nullable=False)
