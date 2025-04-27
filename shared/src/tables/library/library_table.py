from datetime import time
from typing import List

from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from shared.src.core.database import Base
from shared.src.enums import WeekdayEnum
from shared.src.tables import TimeRange
from shared.src.tables.language_table import LanguageTable
from shared.src.tables.like_table import LikeTable
from shared.src.tables.location_table import LocationTable


class LibraryTable(Base):
    __tablename__ = "libraries"
    id = Column(String, primary_key=True)
    hash = Column(String)
    url = Column(String)
    external_url = Column(String, nullable=True)
    reservation_url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)

    location: Mapped["LibraryLocationTable"] = relationship(back_populates="library")
    opening_hours: Mapped["LibraryOpeningHoursTable"] = relationship(back_populates="library")
    translations: Mapped["LibraryTranslationTable"] = relationship(back_populates="library")


class LibraryTranslationTable(LanguageTable):
    __tablename__ = "library_translations"

    library_id = Column(String, ForeignKey("libraries.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String)
    services = Column(JSON)
    equipment = Column(JSON)
    subject_areas = Column(List[String])

    library = relationship("LibraryTable", back_populates="translations")


class LibraryLocationTable(LocationTable):
    __tablename__ = "library_locations"

    library_id = Column(String, ForeignKey("libraries.id", ondelete="CASCADE"), primary_key=True)

    library = relationship("LibraryTable", back_populates="location")


class LibraryLikeTable(LikeTable):
    __tablename__ = "library_likes"

    library_id = Column(String, ForeignKey("libraries.id", ondelete="CASCADE"), primary_key=True)

    library = relationship("LibraryTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_libraries")


class LibraryTimeRange(TimeRange):
    __tablename__ = "library_time_ranges"

    library_opening_hours_id = Column(Integer, ForeignKey("library_opening_hours.id"))

    # Relationship to parent OpeningHours
    library_opening_hours = relationship("LibraryOpeningHoursTable", back_populates="time_ranges")


class LibraryOpeningHoursTable(Base):
    __tablename__ = "library_opening_hours"

    id = Column(Integer, primary_key=True, index=True)
    weekday = Column(Enum(WeekdayEnum), nullable=False)

    # Relationships
    library: Mapped["LibraryTable"] = relationship(
        "LibraryTable", back_populates="opening_hours", cascade="all, delete-orphan"
    )
    time_ranges: Mapped[List[LibraryTimeRange]] = relationship(
        "LibraryTimeRange", back_populates="library_opening_hours", cascade="all, delete-orphan"
    )

    def add_time_range(self, start_time: time, end_time: time) -> LibraryTimeRange:
        """Add a new time range to the opening hours."""
        time_range = LibraryTimeRange(library_opening_hours_id=self.id, start_time=start_time, end_time=end_time)
        self.time_ranges.append(time_range)
        return time_range
