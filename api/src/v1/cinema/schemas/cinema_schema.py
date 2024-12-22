import uuid
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from shared.src.enums import RatingSourceEnum
from shared.src.schemas.location_scheme import Location
from shared.src.schemas import Image
from ...core.schemas.university_scheme import University


class MovieRating(BaseModel):
    source: RatingSourceEnum
    normalized_rating: float
    raw_rating: str
    
class MovieTrailer(BaseModel):
    id: uuid.UUID
    title: str
    published_at: datetime
    url: str
    thumbnail: Image
    site: str

class Movie(BaseModel):
    id: uuid.UUID
    title: str
    tagline: str | None
    overview: str | None
    release_year: date | None
    budget: int | None
    poster: Image | None
    backdrop: Image | None
    runtime: int | None
    genres: List[str]
    ratings: List[MovieRating]
    trailers: List[MovieTrailer]
    
class Cinema(BaseModel):
    id: str
    title: str
    descriptions: List[dict]
    external_link: str | None
    instagram_link: str | None
    location: Location | None
    
class MovieScreening(BaseModel):
    id: uuid.UUID
    entry_time: datetime
    start_time: datetime
    end_time: datetime | None
    price: float | None
    is_ov: bool | None
    subtitles: str | None
    external_link: str | None
    note: str | None
    movie: Movie
    location: Location
    university: University
    cinema: Cinema
    


