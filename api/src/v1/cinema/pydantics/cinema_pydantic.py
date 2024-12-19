from typing import List

from shared.src.tables import (MovieRatingTable, MovieScreeningTable, MovieTable,
                           MovieTrailerTable, MovieTrailerTranslationTable,
                           MovieTranslationTable, CinemaTable)
from ...core.pydantics import (image_to_pydantic, location_to_pydantic,
                                       university_to_pydantic)
from ..schemas.cinema_schema import (Cinema, Movie, MovieRating, MovieScreening,
                                    MovieTrailer)


def movie_ratings_to_pydantic(ratings: List[MovieRatingTable]) -> List[MovieRating]:
    ratings_pydantic = []
    for rating in ratings:
        ratings_pydantic.append(
            MovieRating(
                source=rating.source,
                normalized_rating=rating.normalized_value,
                raw_rating=rating.raw_value,
            )
        )
    return ratings_pydantic
    
def movie_trailers_to_pydantic(trailers: List[MovieTrailerTable]) -> List[MovieTrailer]:
    trailers_pydantic = []
    for trailer in trailers:
        trailer_translations: MovieTrailerTranslationTable = trailer.translations[0] if trailer.translations else None
        title = trailer_translations.title if trailer_translations else "not translated"
        key = trailer_translations.key if trailer_translations else "not translated"
        url = None
        thumbnail_url = None
        
        url = f"https://www.youtube.com/watch?v={key}"
        thumbnail_url = f"https://img.youtube.com/vi/{key}/hqdefault.jpg"
        
        thumbnail = image_to_pydantic(thumbnail_url, f"YouTube Thumbnail for {title}")
        
        trailers_pydantic.append(
            MovieTrailer(
                id=trailer.id,
                title=title,
                published_at=trailer.published_at,
                url=url,    
                thumbnail=thumbnail,
                site=trailer.site,
            )
        )
    return trailers_pydantic



def movie_to_pydantic(movie: MovieTable) -> Movie:
    
    movie_translations: MovieTranslationTable = movie.translations[0] if movie.translations else None
    
    title = movie_translations.title if movie_translations else "not translated"
    overview = movie_translations.overview if movie_translations else "not translated"
    tagline = movie_translations.tagline if movie_translations else "not translated"
    poster = image_to_pydantic(movie_translations.poster_url, "poster") if movie_translations.poster_url else None
    backdrop = image_to_pydantic(movie_translations.backdrop_url, "backdrop") if movie_translations.backdrop_url else None
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
        trailers=trailers,
    )


def movies_to_pydantic(movies: List[MovieTable]) -> List[Movie]:
    return [movie_to_pydantic(movie) for movie in movies]

def cinema_to_pydantic(cinema: CinemaTable) -> Cinema:
    title = cinema.translations[0].title if cinema.translations else "not translated"
    descriptions = cinema.translations[0].description if cinema.translations else "not translated"
    location = location_to_pydantic(cinema.location) if cinema.location else None
    return Cinema(
        id=cinema.id,
        title=title,
        descriptions=descriptions,
        external_link=cinema.external_link,
        instagram_link=cinema.instagram_link,
        location=location,
    )
    
    
def screenings_to_pydantic(screenings: List[MovieScreeningTable]) -> List[MovieScreening]:
    screenings_pydantic = []
    for screening in screenings:
        location = location_to_pydantic(screening.location)
        university = university_to_pydantic(screening.university)
        movie = movie_to_pydantic(screening.movie)
        cinema = cinema_to_pydantic(screening.cinema)
        screenings_pydantic.append(
            MovieScreening(
                id=screening.id,
                entry_time=screening.entry_time,
                start_time=screening.start_time,
                end_time=screening.end_time,
                location=location,
                university=university,
                movie=movie,
                cinema=cinema,
                price=screening.price,
                is_ov=screening.is_ov,
                subtitles=screening.subtitles,
                external_link=screening.external_link,
                booking_link=screening.booking_link,
                note=screening.note,
            )
        )
    return screenings_pydantic