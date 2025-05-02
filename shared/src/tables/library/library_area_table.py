from typing import List

from sqlalchemy import JSON, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from shared.src.core.database import Base
from shared.src.enums import WeekdayEnum
from shared.src.tables.language_table import LanguageTable


class LibraryAreaTable(Base):
    __tablename__ = "library_areas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    library_id = Column(String, ForeignKey("libraries.id", ondelete="CASCADE"))
    opening_hours: Mapped[List["LibraryAreaOpeningHoursTable"]] = relationship(
        "LibraryAreaOpeningHoursTable",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    library = relationship("LibraryTable", back_populates="areas")
    translations: Mapped[List["LibraryAreaTranslationTable"]] = relationship(
        back_populates="area", cascade="all, delete-orphan"
    )


class LibraryAreaTranslationTable(LanguageTable):
    __tablename__ = "library_area_translations"

    area_id = Column(Integer, ForeignKey("library_areas.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String)

    area = relationship("LibraryAreaTable", back_populates="translations")


class LibraryAreaOpeningHoursTable(Base):
    __tablename__ = "library_area_opening_hours"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    area_id = Column(Integer, ForeignKey("library_areas.id", ondelete="CASCADE"))
    weekday = Column(Enum(WeekdayEnum), nullable=False)
    time_ranges = Column(JSON)

    area = relationship("LibraryAreaTable", back_populates="opening_hours")
