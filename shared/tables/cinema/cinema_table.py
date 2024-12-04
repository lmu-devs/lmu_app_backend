import uuid

from sqlalchemy import (UUID, Boolean, Column, Date, DateTime, Enum, Float,
                        ForeignKey, String)
from sqlalchemy.orm import relationship

from shared.database import Base
from shared.tables.image_table import ImageTable
from shared.tables.location_table import LocationTable


class CinemaTable(Base):
    __tablename__ = "cinemas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    external_link = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    
    location = relationship("CinemaLocationTable", back_populates="cinema", uselist=False)
    screenings = relationship("MovieScreeningTable", back_populates="cinema")
    images = relationship("CinemaImageTable", back_populates="cinema")


class CinemaLocationTable(LocationTable, Base):
    __tablename__ = "cinema_locations"
    
    screening_id = Column(UUID(as_uuid=True), ForeignKey("movie_screenings.id", ondelete='CASCADE'), primary_key=True)
    
    screening = relationship("CinemaTable", back_populates="location")
    
class CinemaImageTable(ImageTable, Base):
    __tablename__ = "cinema_images"

    cinema_id = Column(String, ForeignKey('cinemas.id', ondelete='CASCADE'), nullable=False)

    cinema = relationship("CinemaTable", back_populates="images")