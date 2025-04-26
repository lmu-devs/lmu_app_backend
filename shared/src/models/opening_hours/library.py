from typing import List

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from shared.src.db.base_class import Base
from shared.src.models.opening_hours.base import BaseOpeningHours, BaseTimeRangeModel


class LibraryTimeRange(BaseTimeRangeModel):
    __tablename__ = "library_time_ranges"

    opening_hours_id = Column(Integer, ForeignKey("library_opening_hours.id"))
    opening_hours = relationship("LibraryOpeningHours", back_populates="time_ranges")


class LibraryOpeningHours(Base, BaseOpeningHours):
    __tablename__ = "library_opening_hours"

    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)

    # Relationships
    library = relationship("Library", back_populates="opening_hours")
    time_ranges: Mapped[List[LibraryTimeRange]] = relationship(
        "LibraryTimeRange", back_populates="opening_hours", cascade="all, delete-orphan"
    )

    @property
    def time_range_class(self):
        return LibraryTimeRange
