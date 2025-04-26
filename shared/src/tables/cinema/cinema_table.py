from sqlalchemy import ARRAY, JSON, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.image_table import ImageTable
from shared.src.tables.language_table import LanguageTable
from shared.src.tables.location_table import LocationTable


class CinemaTable(Base):
    __tablename__ = "cinemas"

    id = Column(String, primary_key=True)
    external_link = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)

    location = relationship(
        "CinemaLocationTable",
        back_populates="cinema",
        uselist=False,
        cascade="all, delete-orphan",
    )
    translations = relationship("CinemaTranslationTable", back_populates="cinema", cascade="all, delete-orphan")
    images = relationship("CinemaImageTable", back_populates="cinema", cascade="all, delete-orphan")
    screenings = relationship("MovieScreeningTable", back_populates="cinema")


class CinemaImageTable(ImageTable, Base):
    __tablename__ = "cinema_images"

    cinema_id = Column(String, ForeignKey("cinemas.id", ondelete="CASCADE"), nullable=False)

    cinema = relationship("CinemaTable", back_populates="images")


class CinemaLocationTable(LocationTable):
    __tablename__ = "cinema_locations"

    cinema_id = Column(String, ForeignKey("cinemas.id"), primary_key=True)

    cinema = relationship("CinemaTable", back_populates="location")


class CinemaTranslationTable(LanguageTable):
    __tablename__ = "cinema_translations"

    cinema_id = Column(String, ForeignKey("cinemas.id", ondelete="CASCADE"), primary_key=True)
    title = Column(String)
    description = Column(ARRAY(JSON(String)), nullable=True)

    cinema = relationship("CinemaTable", back_populates="translations")
