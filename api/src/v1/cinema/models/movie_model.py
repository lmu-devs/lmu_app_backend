import uuid
from datetime import date
from typing import List

from pydantic import BaseModel, RootModel

from shared.src.models.image_model import Image
from shared.src.tables import MovieTable, MovieTranslationTable

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
    genres: List[str] = []
    ratings: MovieRatings | None
    trailers: MovieTrailers | None
    
    @classmethod
    def from_table(cls, movie: MovieTable) -> 'Movie':
        
        movie_translations: MovieTranslationTable = movie.translations[0] if movie.translations else None
        
        title = movie_translations.title if movie_translations else "not translated"
        overview = movie_translations.overview if movie_translations else "not translated"
        tagline = movie_translations.tagline if movie_translations else "not translated"
        genres = movie_translations.genres if movie_translations and movie_translations.genres else []
        poster = Image.from_params(movie_translations.poster_url, "poster") if movie_translations.poster_url else None
        backdrop = Image.from_params(movie_translations.backdrop_url, "backdrop") if movie_translations.backdrop_url else None
        trailers = MovieTrailers.from_table(movie.trailers)
        ratings = MovieRatings.from_table(movie.ratings)
        
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
            genres=genres,
            runtime=movie.runtime,
            trailers=trailers,
        )


class Movies(RootModel):
    root: List[Movie] | list = []
    
    @classmethod
    def from_table(cls, movies: List[MovieTable]) -> 'Movies':
        return Movies(root=[Movie.from_table(movie) for movie in movies])
