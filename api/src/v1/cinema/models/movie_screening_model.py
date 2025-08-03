import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, RootModel

from shared.src.models.rating_model import Rating
from shared.src.tables import MovieScreeningTable

from .movie_model import Movie


class MovieScreening(BaseModel):
    id: uuid.UUID
    cinema_id: str
    university_id: str
    entry_time: datetime
    start_time: datetime
    end_time: datetime | None
    price: float | None
    is_ov: bool | None
    subtitles: str | None
    external_link: str | None
    note: str | None
    rating: Rating
    movie: Movie

    @classmethod
    def from_table(cls, screening: MovieScreeningTable) -> "MovieScreening":
        movie = Movie.from_table(screening.movie)
        rating = Rating(like_count=screening.like_count, is_liked=screening.is_liked)

        return MovieScreening(
            id=screening.id,
            cinema_id=screening.cinema_id,
            university_id=screening.university_id,
            entry_time=screening.entry_time,
            start_time=screening.start_time,
            end_time=screening.end_time,
            movie=movie,
            price=screening.price,
            is_ov=screening.is_ov,
            subtitles=screening.subtitles,
            external_link=screening.external_link,
            booking_link=screening.booking_link,
            note=screening.note,
            rating=rating,
        )


class MovieScreenings(RootModel):
    root: List[MovieScreening] | list = []

    @classmethod
    def from_table(cls, screenings: List[MovieScreeningTable]) -> "MovieScreenings":
        return MovieScreenings(root=[MovieScreening.from_table(screening) for screening in screenings])
