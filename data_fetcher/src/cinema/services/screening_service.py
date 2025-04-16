import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from data_fetcher.src.cinema.crawler import (
    HmScreeningCrawler,
    LmuScreeningCrawler,
    TumScreeningCrawler,
)
from data_fetcher.src.cinema.models.screening_model import ScreeningCrawl
from data_fetcher.src.cinema.services.omdb_service import OmdbService
from data_fetcher.src.cinema.services.tmdb_service import TmdbService
from data_fetcher.src.cinema.utils.rating_util import MovieRatingNormalizer
from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import LanguageEnum, RatingSourceEnum
from shared.src.tables import (
    MovieLocationTable,
    MovieRatingTable,
    MovieScreeningTable,
    MovieTable,
    MovieTrailerTable,
    MovieTrailerTranslationTable,
    MovieTranslationTable,
)

settings = get_settings()
logger = get_cinema_fetcher_logger(__name__)


class ScreeningService:

    def _create_edge_case_movie_model(self, movie_data: ScreeningCrawl) -> tuple[
        MovieTable,
        list[MovieTranslationTable],
        MovieScreeningTable,
        list[MovieRatingTable],
        list[MovieTrailerTable],
        list[MovieTrailerTranslationTable],
    ]:
        """Create MovieTable and related instances from API data"""

        movie_id = uuid.uuid5(uuid.NAMESPACE_DNS, movie_data.title)
        movie = MovieTable(
            id=movie_id,
            runtime=movie_data.runtime,
            original_title=movie_data.title,
        )

        translation = MovieTranslationTable(
            movie_id=movie_id,
            language=LanguageEnum.GERMAN.value,
            title=movie_data.title,
            tagline=movie_data.tagline,
            overview=movie_data.overview,
            poster_url=movie_data.custom_poster_url,
        )

        end_time = None
        entry_time = None

        if movie_data.runtime:
            end_time = movie_data.date + timedelta(minutes=movie_data.runtime)

        screening_id = uuid.uuid5(
            uuid.NAMESPACE_DNS,
            (movie_data.title + movie_data.cinema_id + str(movie_data.date)),
        )
        entry_time = movie_data.date - timedelta(minutes=30)
        screening = MovieScreeningTable(
            id=screening_id,
            movie_id=movie_id,
            date=movie_data.date,
            university_id=movie_data.cinema_id,
            cinema_id=movie_data.cinema_id,
            start_time=movie_data.date,
            end_time=end_time,
            entry_time=entry_time,
            price=movie_data.price,
            note=movie_data.note,
            location=MovieLocationTable(
                screening_id=screening_id,
                address=movie_data.address,
                longitude=movie_data.longitude,
                latitude=movie_data.latitude,
            ),
        )

        return movie, [translation], screening, [], [], []

    def _create_movie_model(
        self,
        tmdb_data: Dict[Any, Any],
        omdb_data: Dict[Any, Any],
        screening_data: ScreeningCrawl,
    ) -> tuple[
        MovieTable,
        list[MovieTranslationTable],
        MovieScreeningTable,
        list[MovieRatingTable],
        list[MovieTrailerTable],
        list[MovieTrailerTranslationTable],
    ]:
        """Create MovieTable and related instances from API data"""
        tmdb_base_data = tmdb_data[LanguageEnum.ENGLISH_US]

        movie_id = uuid.uuid4()
        movie = MovieTable(
            id=movie_id,
            original_title=tmdb_base_data["original_title"],
            budget=tmdb_base_data.get("budget", 0),
            imdb_id=tmdb_base_data["external_ids"]["imdb_id"],
            popularity=tmdb_base_data.get("popularity", 0.0),
            release_date=datetime.fromisoformat(tmdb_base_data["release_date"]),
            runtime=tmdb_base_data.get("runtime", 0),
            language=tmdb_base_data.get("original_language", "en"),
        )

        # Create screenings
        # TODO: make this dynamic
        screening_id = uuid.uuid4()
        date = screening_data.date.replace(hour=20)
        entry_time = date - timedelta(minutes=30)
        end_time = date + timedelta(minutes=movie.runtime)
        cinema_id = screening_data.cinema_id

        screening = MovieScreeningTable(
            id=screening_id,
            movie_id=movie_id,
            date=date,
            university_id=screening_data.university_id,
            cinema_id=cinema_id,
            start_time=date,
            end_time=end_time,
            entry_time=entry_time,
            price=screening_data.price,
            is_ov=screening_data.is_ov,
            subtitles=screening_data.subtitles,
            external_link=screening_data.external_url,
            location=MovieLocationTable(
                screening_id=screening_id,
                address=screening_data.address,
                longitude=screening_data.longitude,
                latitude=screening_data.latitude,
            ),
        )

        # Create translations
        backdrop_url = tmdb_base_data.get("backdrop_path", "")
        if backdrop_url:
            backdrop_url = f"https://image.tmdb.org/t/p/w1280{backdrop_url}"
        poster_url = tmdb_base_data.get("poster_path", "")
        if poster_url:
            poster_url = f"https://image.tmdb.org/t/p/w1280{poster_url}"

        translations = []

        for lang in LanguageEnum:
            lang_data = tmdb_data[lang]
            genres = lang_data.get("genres", [])
            genres = [genre["name"] for genre in genres]

            translation = MovieTranslationTable(
                movie_id=movie_id,
                language=lang.value,
                title=lang_data["title"],
                overview=lang_data["overview"],
                tagline=lang_data.get("tagline", ""),
                poster_url=poster_url,
                backdrop_url=backdrop_url,
                genres=genres,
            )
            translations.append(translation)

        # Create ratings
        ratings = []
        if omdb_data and "Ratings" in omdb_data:
            for rating_data in omdb_data["Ratings"]:
                source = RatingSourceEnum.from_omdb_source(rating_data["Source"])
                if source:
                    normalized_rating = MovieRatingNormalizer().normalize_rating(source, rating_data["Value"])
                    rating = MovieRatingTable(
                        movie_id=movie_id,
                        source=source,
                        normalized_value=normalized_rating,
                        raw_value=rating_data["Value"],
                    )
                    ratings.append(rating)

        # Create trailers and their translations
        trailers = []
        trailer_translations = []

        # Get trailer data from English response
        base_videos = tmdb_data[LanguageEnum.ENGLISH_US].get("videos", {}).get("results", [])

        for video in base_videos:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                trailer_id = uuid.uuid4()
                trailer = MovieTrailerTable(
                    id=trailer_id,
                    movie_id=movie_id,
                    published_at=datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    official=video["official"],
                    size=video["size"],
                    type=video["type"],
                    site=video["site"],
                )
                trailers.append(trailer)

                # Add translations for each language
                for lang in LanguageEnum:
                    # Find matching video in language-specific response
                    lang_videos = tmdb_data[lang].get("videos", {}).get("results", [])
                    matching_video = next(
                        (v for v in lang_videos if v["id"] == video["id"]),
                        video,  # Fallback to English if no translation exists
                    )

                    translation = MovieTrailerTranslationTable(
                        trailer_id=trailer_id,
                        language=lang.value,
                        title=matching_video["name"],
                        key=matching_video["key"],
                    )
                    trailer_translations.append(translation)

        return movie, translations, screening, ratings, trailers, trailer_translations

    async def fetch_and_process_movies(
        self,
    ) -> list[
        tuple[
            MovieTable,
            list[MovieTranslationTable],
            MovieScreeningTable,
            list[MovieRatingTable],
            list[MovieTrailerTable],
            list[MovieTrailerTranslationTable],
        ]
    ]:
        """Fetch LMU movies and enrich with TMDB and OMDB data"""
        logger.info("Starting movie fetch process")

        crawled_movies: list[ScreeningCrawl] = []
        crawled_movies.extend(LmuScreeningCrawler().crawl())
        crawled_movies.extend(TumScreeningCrawler().crawl())
        crawled_movies.extend(HmScreeningCrawler().crawl())

        processed_movies = []

        for crawled_movie in crawled_movies:

            logger.info(f"Processing movie: {crawled_movie.title}")

            if crawled_movie.is_edge_case:
                processed_movies.append(self._create_edge_case_movie_model(crawled_movie))

            else:
                tmdb_service = TmdbService()
                tmdb_data = tmdb_service.search_tmdb_movie(crawled_movie.title, crawled_movie.year)
                if not tmdb_data:
                    logger.warning(f"Could not find TMDB data for {crawled_movie.title}")
                    continue

                imdb_id = tmdb_data[LanguageEnum.ENGLISH_US]["external_ids"]["imdb_id"]
                omdb_service = OmdbService()
                omdb_data = omdb_service.get_omdb_data(imdb_id)
                if not omdb_data:
                    logger.warning(f"Could not find OMDB data for {crawled_movie.title}")
                    continue

                (
                    crawled_movie,
                    translations,
                    screenings,
                    ratings,
                    trailers,
                    trailer_translations,
                ) = self._create_movie_model(tmdb_data, omdb_data, crawled_movie)
                processed_movies.append(
                    (
                        crawled_movie,
                        translations,
                        screenings,
                        ratings,
                        trailers,
                        trailer_translations,
                    )
                )

                logger.info(f"Successfully processed {crawled_movie.original_title}")

        logger.info(f"Completed processing {len(processed_movies)} movies")
        return processed_movies
