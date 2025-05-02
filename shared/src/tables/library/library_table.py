from typing import List

from sqlalchemy import ARRAY, JSON, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from shared.src.core.database import Base
from shared.src.tables.language_table import LanguageTable
from shared.src.tables.library.library_area_table import LibraryAreaTable
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
    areas: Mapped[List["LibraryAreaTable"]] = relationship(
        "LibraryAreaTable",
        back_populates="library",
        cascade="all, delete-orphan",
    )
    translations: Mapped[List["LibraryTranslationTable"]] = relationship(
        back_populates="library", cascade="all, delete-orphan"
    )
    likes = relationship("LibraryLikeTable", back_populates="library")

    @property
    def like_count(self):
        return len(self.likes)


class LibraryTranslationTable(LanguageTable):
    __tablename__ = "library_translations"

    library_id = Column(String, ForeignKey("libraries.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String)
    services = Column(JSON)
    equipment = Column(JSON)
    subject_areas = Column(ARRAY(String))

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
