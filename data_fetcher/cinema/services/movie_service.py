import uuid

from datetime import datetime, timedelta
from typing import Any, Dict

from shared.core.logging import get_movie_fetcher_logger
from shared.settings import get_settings
from shared.enums.language_enums import LanguageEnum
from shared.enums.rating_enums import RatingSourceEnum
from shared.tables.cinema.movie_table import (MovieLocationTable, MovieRatingTable,
                                       MovieScreeningTable, MovieTable,
                                       MovieTrailerTable,
                                       MovieTrailerTranslationTable,
                                       MovieTranslationTable)
from ..models.movie_model import ScreeningCrawl
from ..utils.rating_util import MovieRatingNormalizer
from ..crawler.lmu_movie_crawler import LmuMovieCrawler
from ..crawler.tum_movie_crawler import TumMovieCrawler
from .omdb_service import OmdbService
from .tmdb_service import TmdbService

settings = get_settings()
logger = get_movie_fetcher_logger(__name__)

class MovieService:
    
    def _create_movie_model(self, tmdb_data: Dict[Any, Any], omdb_data: Dict[Any, Any], movie_data: ScreeningCrawl) -> tuple[MovieTable, list[MovieTranslationTable], MovieScreeningTable, list[MovieRatingTable], list[MovieTrailerTable], list[MovieTrailerTranslationTable]]:
        """Create MovieTable and related instances from API data"""
        base_data = tmdb_data[LanguageEnum.ENGLISH_US]
    
        movie_id = uuid.uuid4()
        movie = MovieTable(
            id=movie_id,
            original_title=base_data["original_title"],
            budget=base_data.get("budget", 0),
            imdb_id=base_data["external_ids"]["imdb_id"],
            popularity=base_data.get("popularity", 0.0),
            release_date=datetime.fromisoformat(base_data["release_date"]),
            runtime=base_data.get("runtime", 0),
            language=base_data.get("original_language", "en"),
            homepage=base_data.get("homepage", ""),
        )
        
        # Create screenings
        # TODO: make this dynamic
        screening_id = uuid.uuid4()
        date = movie_data.date.replace(hour=20)
        entry_time = date - timedelta(minutes=30)
        end_time = date + timedelta(minutes=movie.runtime)
        university_id = movie_data.university_id
        
        screening = MovieScreeningTable(
            id=screening_id,
            movie_id=movie_id,
            date=date,
            university_id=university_id,
            start_time=date,
            end_time=end_time,
            entry_time=entry_time,
            price=movie_data.price,
            is_ov=movie_data.is_ov,
            subtitles=movie_data.subtitles,
            external_link=movie_data.external_link,
            location=MovieLocationTable(
                screening_id=screening_id,
                address=movie_data.address,
                longitude=movie_data.longitude,
                latitude=movie_data.latitude
            )
        )

        # Create translations
        backdrop_path = base_data.get("backdrop_path", "")
        if backdrop_path:
            backdrop_path = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        poster_path = base_data.get("poster_path", "")
        if poster_path:
            poster_path = f"https://image.tmdb.org/t/p/w1280{poster_path}"
            
        translations = []
        
        for lang in LanguageEnum:
            lang_data = tmdb_data[lang]
            translation = MovieTranslationTable(
                movie_id=movie_id,
                language=lang.value,
                title=lang_data["title"],
                overview=lang_data["overview"],
                tagline=lang_data.get("tagline", ""),
                poster_path=poster_path,
                backdrop_path=backdrop_path,
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
                        raw_value=rating_data["Value"]
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
                    site=video["site"]
                )
                trailers.append(trailer)
                
                # Add translations for each language
                for lang in LanguageEnum:
                    # Find matching video in language-specific response
                    lang_videos = tmdb_data[lang].get("videos", {}).get("results", [])
                    matching_video = next(
                        (v for v in lang_videos if v["id"] == video["id"]), 
                        video  # Fallback to English if no translation exists
                    )
                    
                    translation = MovieTrailerTranslationTable(
                        trailer_id=trailer_id,
                        language=lang.value,
                        title=matching_video["name"],
                        key=matching_video["key"]
                    )
                    trailer_translations.append(translation)

        return movie, translations, screening, ratings, trailers, trailer_translations

    async def fetch_and_process_movies(self) -> list[tuple[MovieTable, list[MovieTranslationTable], MovieScreeningTable, list[MovieRatingTable], list[MovieTrailerTable], list[MovieTrailerTranslationTable]]]:
        """Fetch LMU movies and enrich with TMDB and OMDB data"""
        logger.info("Starting movie fetch process")
        
        crawled_movies: list[ScreeningCrawl] = []
        crawled_movies.extend(LmuMovieCrawler().crawl())
        crawled_movies.extend(TumMovieCrawler().crawl())
        # TODO: HM crawler
            
        processed_movies = []

        for crawled_movie in crawled_movies:

            logger.info(f"Processing movie: {crawled_movie.title}")
            
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

            crawled_movie, translations, screenings, ratings, trailers, trailer_translations = self._create_movie_model(tmdb_data, omdb_data, crawled_movie)
            processed_movies.append((crawled_movie, translations, screenings, ratings, trailers, trailer_translations))
            
            logger.info(f"Successfully processed {crawled_movie.original_title}")

        logger.info(f"Completed processing {len(processed_movies)} movies")
        return processed_movies 