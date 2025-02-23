from typing import List
import uuid

from datetime import datetime
from pydantic import BaseModel, RootModel

from shared.src.tables import MovieScreeningTable
from ...core.models.university_scheme import University
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
    movie: Movie
    
    @classmethod
    def from_table(cls, screening: MovieScreeningTable) -> 'MovieScreening':
        movie = Movie.from_table(screening.movie)
        
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
        )
    
    
    
class MovieScreenings(RootModel):
    root: List[MovieScreening] | list = []
    
    @classmethod
    def from_table(cls, screenings: List[MovieScreeningTable]) -> 'MovieScreenings':
        return MovieScreenings(root=[MovieScreening.from_table(screening) for screening in screenings])
