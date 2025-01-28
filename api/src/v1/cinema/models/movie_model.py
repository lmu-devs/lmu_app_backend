import uuid
from datetime import date, datetime
from typing import List

from pydantic import BaseModel


from shared.src.tables import MovieTable, MovieTranslationTable
from shared.src.models.image_model import Image
from .movie_rating_model import MovieRatings
from .movie_trailer_model import MovieTrailers


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
    ratings: MovieRatings | None
    trailers: MovieTrailers | None
    
    @classmethod
    def from_table(cls, movie: MovieTable) -> 'Movie':
        
        movie_translations: MovieTranslationTable = movie.translations[0] if movie.translations else None
        
        title = movie_translations.title if movie_translations else "not translated"
        overview = movie_translations.overview if movie_translations else "not translated"
        tagline = movie_translations.tagline if movie_translations else "not translated"
        poster = Image.from_params(movie_translations.poster_url, "poster") if movie_translations.poster_url else None
        backdrop = Image.from_params(movie_translations.backdrop_url, "backdrop") if movie_translations.backdrop_url else None
        trailers = MovieTrailers.from_table(movie.trailers) if movie.trailers else []
        ratings = MovieRatings.from_table(movie.ratings) if movie.ratings else []
        
        return Movie(
            id=movie.id,
            title=title,
            overview=overview,
            tagline=tagline,
            release_year=movie.release_date,
            budget=movie.budget,
            ratings=ratings,
            poster=poster,
            backdrop=backdrop,
            genres=movie.genres,
            runtime=movie.runtime,
            trailers=trailers,
        )



class Movies(BaseModel):
    movies: List[Movie]
    
    @classmethod
    def from_table(cls, movies: List[MovieTable]) -> 'Movies':
        return Movies(movies=[Movie.movie_to_pydantic(movie) for movie in movies])
