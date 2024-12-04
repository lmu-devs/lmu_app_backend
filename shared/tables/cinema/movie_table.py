import uuid

from sqlalchemy import (UUID, Boolean, Column, Date, DateTime, Enum, Float,
                        ForeignKey, Integer, String, Table, UniqueConstraint)
from sqlalchemy.orm import relationship

from shared.database import Base
from shared.enums.rating_enums import RatingSourceEnum
from shared.tables.language_table import LanguageTable
from shared.tables.location_table import LocationTable

# Association table for the many-to-many relationship between movies and genres
movie_genre_association = Table(
    'movie_genre_associations', Base.metadata,
    Column('movie_id', UUID(as_uuid=True), ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', UUID(as_uuid=True), ForeignKey('movie_genres.id', ondelete='CASCADE'), primary_key=True)
)

class MovieScreeningTable(Base):
    __tablename__ = "movie_screenings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id", ondelete='CASCADE'))
    university_id = Column(String, ForeignKey("universities.id", ondelete='CASCADE'))
    entry_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    price = Column(Float, nullable=True)
    external_link = Column(String, nullable=True)
    booking_link = Column(String, nullable=True)
    is_ov = Column(Boolean, nullable=True)
    subtitles = Column(String, nullable=True)
    
    movie = relationship("MovieTable", back_populates="screenings")
    university = relationship("UniversityTable", back_populates="screenings")
    cinema = relationship("CinemaTable", back_populates="screenings")
    location = relationship("MovieLocationTable", back_populates="screening", uselist=False)
    
    __table_args__ = (
        UniqueConstraint('date', 'movie_id', name='uix_date_movie_id'),
    )
    
class MovieLocationTable(LocationTable, Base):
    __tablename__ = "movie_locations"
    
    screening_id = Column(UUID(as_uuid=True), ForeignKey("movie_screenings.id", ondelete='CASCADE'), primary_key=True)
    
    screening = relationship("MovieScreeningTable", back_populates="location")
    
    
class MovieTable(Base):
    __tablename__ = "movies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_title = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    budget = Column(Integer, nullable=False)
    imdb_id = Column(String, nullable=False)
    popularity = Column(Float, nullable=False)
    runtime = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    homepage = Column(String, nullable=False)
    
    translations = relationship("MovieTranslationTable", back_populates="movie", cascade="all, delete-orphan")
    genres = relationship("MovieGenreTable", secondary=movie_genre_association, back_populates="movies")
    screenings = relationship("MovieScreeningTable", back_populates="movie", cascade="all, delete-orphan")
    ratings = relationship("MovieRatingTable", back_populates="movie", cascade="all, delete-orphan")
    trailers = relationship("MovieTrailerTable", back_populates="movie", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('original_title', 'release_date', name='uix_original_title_release_date'),
    )
    
class MovieTranslationTable(LanguageTable, Base):
    __tablename__ = "movie_translations"
    
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id", ondelete='CASCADE'), primary_key=True)
    language = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    overview = Column(String, nullable=False)
    tagline = Column(String, nullable=False)
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    
    movie = relationship("MovieTable", back_populates="translations")


class MovieGenreTable(Base):
    __tablename__ = "movie_genres"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    movies = relationship("MovieTable", secondary=movie_genre_association, back_populates="genres")

class MovieRatingTable(Base):
    __tablename__ = "movie_ratings"

    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"), primary_key=True)
    source = Column(Enum(RatingSourceEnum), primary_key=True)
    normalized_value = Column(Float, nullable=False)
    raw_value = Column(String, nullable=False)
    
    movie = relationship("MovieTable", back_populates="ratings")


class MovieTrailerTable(Base):
    __tablename__ = "movie_trailers"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movies.id"))
    published_at = Column(DateTime, nullable=False)
    official = Column(Boolean, nullable=False)
    size = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    site = Column(String, nullable=False)
    
    movie = relationship("MovieTable", back_populates="trailers")
    translations = relationship("MovieTrailerTranslationTable", back_populates="trailer", cascade="all, delete-orphan")
    
    
class MovieTrailerTranslationTable(LanguageTable, Base):
    __tablename__ = "movie_trailer_translations"
    
    trailer_id = Column(UUID(as_uuid=True), ForeignKey("movie_trailers.id"), primary_key=True)
    title = Column(String, nullable=False)
    key = Column(String, nullable=False)
    
    trailer = relationship("MovieTrailerTable", back_populates="translations")
