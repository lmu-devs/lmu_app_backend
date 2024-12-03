from typing import List

from api.v1.core.pydantics import image_to_pydantic, location_to_pydantic
from shared.tables import (MovieRatingTable, MovieScreeningTable, MovieTable,
                           MovieTrailerTable, MovieTrailerTranslationTable,
                           MovieTranslationTable)

from ..schemas.movie_schema import (Movie, MovieRating, MovieScreening,
                                    MovieTrailer)


def movie_ratings_to_pydantic(ratings: List[MovieRatingTable]) -> List[MovieRating]:
    ratings_pydantic = []
    for rating in ratings:
        ratings_pydantic.append(MovieRating(
            source=rating.source,
        normalized_rating=rating.normalized_value,
            raw_rating=rating.raw_value,
        ))
    return ratings_pydantic
    
def movie_trailers_to_pydantic(trailers: List[MovieTrailerTable]) -> List[MovieTrailer]:
    trailers_pydantic = []
    for trailer in trailers:
        trailer_translations: MovieTrailerTranslationTable = trailer.translations[0] if trailer.translations else None
        title = trailer_translations.title if trailer_translations else "not translated"
        key = trailer_translations.key if trailer_translations else "not translated"

        print(key)
        url = None
        thumbnail_url = None
        
        url = f"https://www.youtube.com/watch?v={key}"
        thumbnail_url = f"https://img.youtube.com/vi/{key}/hqdefault.jpg"
        
        thumbnail = image_to_pydantic(thumbnail_url, f"YouTube Thumbnail for {title}")
        
        trailers_pydantic.append(MovieTrailer(
            id=trailer.id,
            title=title,
            published_at=trailer.published_at,
            url=url,    
            thumbnail=thumbnail,
            site=trailer.site,
        ))
    return trailers_pydantic



def movie_to_pydantic(movie: MovieTable) -> Movie:
    
    movie_translations: MovieTranslationTable = movie.translations[0] if movie.translations else None
    
    title = movie_translations.title if movie_translations else "not translated"
    overview = movie_translations.overview if movie_translations else "not translated"
    tagline = movie_translations.tagline if movie_translations else "not translated"
    poster = image_to_pydantic(movie_translations.poster_path, "poster") if movie_translations else "not translated"
    backdrop = image_to_pydantic(movie_translations.backdrop_path, "backdrop") if movie_translations else "not translated"
    
    
    
    trailers = movie_trailers_to_pydantic(movie.trailers)
    ratings = movie_ratings_to_pydantic(movie.ratings)
    
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
        homepage=movie.homepage,
        trailers=trailers,
    )
    
def movies_to_pydantic(movies: List[MovieTable]) -> List[Movie]:
    movies_pydantic = []
    for movie in movies:
        movies_pydantic.append(movie_to_pydantic(movie))
    return movies_pydantic
    
def screenings_to_pydantic(screenings: List[MovieScreeningTable]) -> List[MovieScreening]:
    screenings_pydantic = []
    for screening in screenings:
        location = location_to_pydantic(screening.address)
        screenings_pydantic.append(MovieScreening(
            movie=movie_to_pydantic(screening.movie),
            entry_time=screening.entry_time,
            start_time=screening.start_time,
            end_time=screening.end_time,
            location=location
        ))
    return screenings_pydantic