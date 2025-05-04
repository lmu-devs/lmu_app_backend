import uuid

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.enums import UniversityEnum
from shared.src.tables.like_table import LikeTable
from shared.src.tables.location_table import LocationTable


class MovieScreeningTable(Base):
    __tablename__ = "movie_screenings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"))
    university_id = Column(Enum(UniversityEnum), ForeignKey("universities.id", ondelete="CASCADE"))
    cinema_id = Column(String, ForeignKey("cinemas.id", ondelete="CASCADE"))
    entry_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    price = Column(Float, nullable=True)
    external_link = Column(String, nullable=True)
    booking_link = Column(String, nullable=True)
    is_ov = Column(Boolean, nullable=True)
    subtitles = Column(String, nullable=True)
    note = Column(String, nullable=True)

    movie = relationship("MovieTable", back_populates="screenings")
    university = relationship("UniversityTable", back_populates="screenings")
    cinema = relationship("CinemaTable", back_populates="screenings")
    location = relationship("MovieLocationTable", back_populates="screening", uselist=False)
    likes = relationship("ScreeningLikeTable", back_populates="screening")

    # not stored in the database
    @property
    def like_count(self):
        return len(self.likes)

    is_liked = False

    __table_args__ = (UniqueConstraint("date", "movie_id", name="uix_date_movie_id"),)


class MovieLocationTable(LocationTable):
    __tablename__ = "movie_locations"

    screening_id = Column(
        UUID(as_uuid=True),
        ForeignKey("movie_screenings.id", ondelete="CASCADE"),
        primary_key=True,
    )

    screening = relationship("MovieScreeningTable", back_populates="location")


class ScreeningLikeTable(LikeTable):
    __tablename__ = "movie_screening_likes"

    movie_screening_id = Column(
        UUID(as_uuid=True),
        ForeignKey("movie_screenings.id", ondelete="CASCADE"),
        primary_key=True,
    )

    screening = relationship("MovieScreeningTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_screenings")
